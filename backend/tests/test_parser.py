"""Unit tests for the GGPoker hand history parser."""
import pytest
from app.parser.ggpoker_parser import GGPokerParser
from app.parser.splitter import split_hands

_parser = GGPokerParser()


class TestSplitter:
    def test_single_hand_returns_one_block(self, normal_hand_text):
        blocks = split_hands(normal_hand_text)
        assert len(blocks) == 1

    def test_multi_hand_splits_correctly(self, multi_hand_text):
        blocks = split_hands(multi_hand_text)
        assert len(blocks) == 2

    def test_each_block_starts_with_hand_header(self, multi_hand_text):
        for block in split_hands(multi_hand_text):
            assert block.startswith("Poker Hand #")

    def test_empty_string_returns_empty_list(self):
        assert split_hands("") == []

    def test_whitespace_only_returns_empty_list(self):
        assert split_hands("   \n\n  ") == []


class TestHeaderParsing:
    def test_hand_id_parsed(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.ggpoker_hand_id == "HD1111111111"

    def test_stakes_parsed(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.stakes_sb == pytest.approx(0.05)
        assert hand.stakes_bb == pytest.approx(0.10)

    def test_game_type_normalized(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.game_type == "NLH"

    def test_datetime_parsed(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.played_at.year == 2024
        assert hand.played_at.month == 1
        assert hand.played_at.day == 15


class TestTableAndSeats:
    def test_table_name_parsed(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.table_name == "Rush&Cash1"

    def test_button_seat_parsed(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.button_seat == 3

    def test_six_players_detected(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.num_players == 6
        assert len(hand.players) == 6

    def test_player_stacks_parsed(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        hero = next(p for p in hand.players if p.name == "Hero")
        assert hero.stack_chips == pytest.approx(10.50)


class TestHoleCards:
    def test_hero_identified(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.hero_name == "Hero"

    def test_hero_cards_parsed(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.hero_cards == "Ah Kd"

    def test_hero_seat_set(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.hero_seat == 1


class TestActionParsing:
    def test_fast_fold_action_detected(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        fast_folds = [a for a in hand.actions if a.action_type == "FAST_FOLD"]
        assert len(fast_folds) == 2  # Villain1 and Villain5

    def test_raise_action_parsed(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        raises = [a for a in hand.actions if a.action_type == "RAISE"]
        assert len(raises) == 1
        assert raises[0].player_name == "Hero"
        assert raises[0].amount_chips == pytest.approx(0.30)

    def test_bet_action_parsed(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        bets = [a for a in hand.actions if a.action_type == "BET"]
        assert len(bets) == 1
        assert bets[0].street == "FLOP"

    def test_fold_action_without_fast_fold(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        normal_folds = [
            a for a in hand.actions
            if a.action_type == "FOLD" and a.player_name in ("Villain3", "Villain4")
        ]
        assert len(normal_folds) == 2

    def test_call_action_parsed(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        calls = [a for a in hand.actions if a.action_type == "CALL"]
        assert any(a.player_name == "Villain2" for a in calls)

    def test_action_sequence_is_monotonically_increasing(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        seqs = [a.sequence for a in hand.actions]
        assert seqs == sorted(seqs)
        assert len(seqs) == len(set(seqs))  # no duplicates


class TestBoardParsing:
    def test_flop_parsed(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.flop_cards == "7h 8c As"

    def test_no_turn_when_hand_ends_on_flop(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.turn_card is None
        assert hand.river_card is None

    def test_full_board_parsed(self, showdown_hand_text):
        hand = _parser.parse(showdown_hand_text)
        assert hand.flop_cards == "Kh 8d 2s"
        assert hand.turn_card == "Ac"
        assert hand.river_card == "3d"


class TestRunItTwice:
    def test_run_it_twice_flagged(self, run_it_twice_hand_text):
        hand = _parser.parse(run_it_twice_hand_text)
        assert hand.run_it_twice is True

    def test_normal_hand_not_run_it_twice(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.run_it_twice is False


class TestShowdown:
    def test_showdown_cards_recorded(self, showdown_hand_text):
        hand = _parser.parse(showdown_hand_text)
        hero_player = next(p for p in hand.players if p.name == "Hero")
        assert hero_player.hole_cards == "Ac Kc"

    def test_villain_showdown_cards_recorded(self, showdown_hand_text):
        hand = _parser.parse(showdown_hand_text)
        villain = next(p for p in hand.players if p.name == "Villain3")
        assert villain.hole_cards is not None


class TestAllIn:
    def test_all_in_flag_set(self, run_it_twice_hand_text):
        hand = _parser.parse(run_it_twice_hand_text)
        all_in_actions = [a for a in hand.actions if a.is_all_in]
        assert len(all_in_actions) >= 1

    def test_pot_total_parsed(self, normal_hand_text):
        hand = _parser.parse(normal_hand_text)
        assert hand.pot_total_chips == pytest.approx(0.78)
        assert hand.rake_chips == pytest.approx(0.03)
