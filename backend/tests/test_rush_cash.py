"""Tests for Rush & Cash stat computation logic."""
import pytest
from app.parser.ggpoker_parser import GGPokerParser
from app.parser.rush_cash import compute_stats

_parser = GGPokerParser()


def parse_and_compute(text: str):
    hand = _parser.parse(text)
    assert hand is not None
    compute_stats(hand)
    return hand


class TestFastFold:
    def test_hero_fast_fold_detected(self, fast_fold_hand_text):
        hand = parse_and_compute(fast_fold_hand_text)
        assert hand.is_fast_fold is True

    def test_hero_fast_fold_is_not_vpip(self, fast_fold_hand_text):
        hand = parse_and_compute(fast_fold_hand_text)
        assert hand.hero_vpip is False

    def test_hero_fast_fold_is_not_pfr(self, fast_fold_hand_text):
        hand = parse_and_compute(fast_fold_hand_text)
        assert hand.hero_pfr is False

    def test_normal_hand_is_not_fast_fold(self, normal_hand_text):
        hand = parse_and_compute(normal_hand_text)
        assert hand.is_fast_fold is False


class TestVPIP:
    def test_hero_raise_counts_as_vpip(self, normal_hand_text):
        hand = parse_and_compute(normal_hand_text)
        assert hand.hero_vpip is True

    def test_hero_call_counts_as_vpip(self, showdown_hand_text):
        hand = parse_and_compute(showdown_hand_text)
        # Hero calls a 3bet in this hand
        assert hand.hero_vpip is True

    def test_hero_fold_is_not_vpip(self, fast_fold_hand_text):
        hand = parse_and_compute(fast_fold_hand_text)
        assert hand.hero_vpip is False


class TestPFR:
    def test_hero_raise_counts_as_pfr(self, normal_hand_text):
        hand = parse_and_compute(normal_hand_text)
        assert hand.hero_pfr is True

    def test_hero_raise_counts_as_pfr_in_showdown_hand(self, showdown_hand_text):
        hand = parse_and_compute(showdown_hand_text)
        # Hero opens with a raise preflop in this hand → PFR True
        assert hand.hero_pfr is True

    def test_hero_call_is_not_pfr(self, bb_call_hand_text):
        hand = parse_and_compute(bb_call_hand_text)
        # Hero is BB and just calls an open raise → PFR False
        assert hand.hero_pfr is False

    def test_hero_fast_fold_is_not_pfr(self, fast_fold_hand_text):
        hand = parse_and_compute(fast_fold_hand_text)
        assert hand.hero_pfr is False


class TestThreeBet:
    def test_hero_facing_raise_has_3bet_opportunity(self, bb_call_hand_text):
        hand = parse_and_compute(bb_call_hand_text)
        # Hero is BB, Villain2 open-raises before Hero acts → 3bet opportunity
        # Hero calls → had the opportunity but did not take it
        assert hand.hero_had_3bet_opportunity is True
        assert hand.hero_3bet is False

    def test_hero_open_raise_no_3bet_opportunity(self, normal_hand_text):
        hand = parse_and_compute(normal_hand_text)
        # Hero is first to raise, nobody raised before Hero → no 3bet opportunity
        assert hand.hero_had_3bet_opportunity is False


class TestSawFlop:
    def test_hero_saw_flop_when_played_through(self, normal_hand_text):
        hand = parse_and_compute(normal_hand_text)
        assert hand.hero_saw_flop is True

    def test_hero_did_not_see_flop_when_fast_folded(self, fast_fold_hand_text):
        hand = parse_and_compute(fast_fold_hand_text)
        assert hand.hero_saw_flop is False


class TestShowdownStats:
    def test_went_to_showdown(self, showdown_hand_text):
        hand = parse_and_compute(showdown_hand_text)
        assert hand.hero_went_to_showdown is True

    def test_did_not_go_to_showdown(self, normal_hand_text):
        hand = parse_and_compute(normal_hand_text)
        assert hand.hero_went_to_showdown is False


class TestAggression:
    def test_bet_raise_count(self, normal_hand_text):
        hand = parse_and_compute(normal_hand_text)
        # Hero: raises preflop (1) + bets flop (1) = 2
        assert hand.hero_bet_raise_count == 2

    def test_call_count(self, showdown_hand_text):
        hand = parse_and_compute(showdown_hand_text)
        # Hero calls preflop 3bet + calls flop + calls turn = at least 2 calls
        assert hand.hero_call_count >= 2


class TestPositions:
    def test_position_assigned(self, normal_hand_text):
        hand = parse_and_compute(normal_hand_text)
        assert hand.hero_position is not None

    def test_button_seat_3_gives_correct_positions(self, normal_hand_text):
        hand = parse_and_compute(normal_hand_text)
        # Button = seat 3 → seat 4 = SB, seat 5 = BB, seat 6 = UTG, seat 1 = HJ, seat 2 = CO
        seat_pos = {p.seat: None for p in hand.players}
        # Hero at seat 1 should be HJ in 6-handed with button at seat 3
        assert hand.hero_position == "HJ"
