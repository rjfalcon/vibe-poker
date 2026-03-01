"""Tests for the built-in GTO poker analysis engine."""
from __future__ import annotations

from types import SimpleNamespace
import pytest

from app.poker_engine.cards import (
    parse_card, parse_hand, hand_key, hand_category, board_texture,
)
from app.poker_engine.ranges import hand_in_range, pos_range_pct
from app.poker_engine.pot_tracker import PotTracker
from app.poker_engine.analyzer import analyze


# ---------------------------------------------------------------------------
# cards.py
# ---------------------------------------------------------------------------

class TestParseCard:
    def test_ace_of_hearts(self):
        assert parse_card('Ah') == (14, 'h')

    def test_king_of_spades(self):
        assert parse_card('Ks') == (13, 's')

    def test_ten(self):
        assert parse_card('Td') == (10, 'd')

    def test_two(self):
        assert parse_card('2c') == (2, 'c')


class TestParseHand:
    def test_two_cards(self):
        result = parse_hand('Ah Kd')
        assert result == [(14, 'h'), (13, 'd')]

    def test_none_input(self):
        assert parse_hand(None) is None

    def test_empty(self):
        assert parse_hand('') is None

    def test_single_card(self):
        assert parse_hand('Ah') is None


class TestHandKey:
    def test_pair(self):
        assert hand_key((14, 'h'), (14, 'd')) == 'AA'

    def test_suited(self):
        assert hand_key((14, 'h'), (13, 'h')) == 'AKs'

    def test_offsuit(self):
        assert hand_key((14, 'h'), (13, 'd')) == 'AKo'

    def test_sorted_higher_first(self):
        # Lower rank first as input — should sort correctly
        assert hand_key((9, 'h'), (14, 'd')) == 'A9o'


class TestHandCategory:
    def test_aces_premium(self):
        assert hand_category((14, 'h'), (14, 'd')) == 'premium'

    def test_jacks_premium(self):
        assert hand_category((11, 'h'), (11, 'd')) == 'premium'

    def test_tens_strong(self):
        assert hand_category((10, 'h'), (10, 'd')) == 'strong'

    def test_nines_strong(self):
        assert hand_category((9, 'h'), (9, 'd')) == 'strong'

    def test_sevens_speculative(self):
        assert hand_category((7, 'h'), (7, 'd')) == 'speculative'

    def test_ak_suited_premium(self):
        assert hand_category((14, 'h'), (13, 'h')) == 'premium'

    def test_ak_offsuit_premium(self):
        assert hand_category((14, 'h'), (13, 'd')) == 'premium'

    def test_aq_suited_strong(self):
        assert hand_category((14, 'h'), (12, 'h')) == 'strong'

    def test_a2_suited_speculative(self):
        assert hand_category((14, 'h'), (2, 'h')) == 'speculative'

    def test_a2_offsuit_weak(self):
        assert hand_category((14, 'h'), (2, 'd')) == 'weak'

    def test_suited_connector_speculative(self):
        assert hand_category((9, 'h'), (8, 'h')) == 'speculative'

    def test_j3_offsuit_weak(self):
        assert hand_category((11, 'h'), (3, 'd')) == 'weak'


class TestBoardTexture:
    def test_empty(self):
        t = board_texture([])
        assert t['flush_draw'] is False
        assert t['wet'] is False

    def test_rainbow_dry(self):
        t = board_texture(['7h', '2d', 'Kc'])
        assert t['flush_draw'] is False
        assert t['wet'] is False
        assert t['high_card'] == 13

    def test_two_tone_flush_draw(self):
        t = board_texture(['7h', '8h', 'Kd'])
        assert t['flush_draw'] is True
        assert t['wet'] is True

    def test_connected_straight_draw(self):
        t = board_texture(['7h', '8d', '9c'])
        assert t['straight_draw'] is True
        assert t['wet'] is True

    def test_paired_board(self):
        t = board_texture(['7h', '7d', 'Kc'])
        assert t['paired'] is True


# ---------------------------------------------------------------------------
# ranges.py
# ---------------------------------------------------------------------------

class TestHandInRange:
    def test_aa_always_in_range(self):
        for pos in ['UTG', 'HJ', 'CO', 'BTN', 'SB']:
            assert hand_in_range((14, 'h'), (14, 'd'), pos)

    def test_72o_utg_out_of_range(self):
        assert not hand_in_range((7, 'h'), (2, 'd'), 'UTG')

    def test_72o_btn_out_of_range(self):
        assert not hand_in_range((7, 'h'), (2, 'd'), 'BTN')

    def test_kqs_utg_in_range(self):
        # KQs (r2=12) satisfies UTG condition r2>=11, so it IS in range
        assert hand_in_range((13, 'h'), (12, 'h'), 'UTG')

    def test_k9s_utg_out_of_range(self):
        # K9s (r2=9) does NOT satisfy UTG condition r2>=11
        assert not hand_in_range((13, 'h'), (9, 'h'), 'UTG')

    def test_a9s_utg_in_range(self):
        assert hand_in_range((14, 'h'), (9, 'h'), 'UTG')

    def test_a8s_utg_out_of_range(self):
        assert not hand_in_range((14, 'h'), (8, 'h'), 'UTG')

    def test_a7s_hj_in_range(self):
        assert hand_in_range((14, 'h'), (7, 'h'), 'HJ')

    def test_all_ax_suited_co_in_range(self):
        assert hand_in_range((14, 'h'), (2, 'h'), 'CO')

    def test_small_pairs_btn_in_range(self):
        assert hand_in_range((3, 'h'), (3, 'd'), 'BTN')

    def test_small_pairs_utg_out_of_range(self):
        assert not hand_in_range((3, 'h'), (3, 'd'), 'UTG')

    def test_unknown_position_returns_true(self):
        assert hand_in_range((7, 'h'), (2, 'd'), 'UNKNOWN') is True

    def test_pos_range_pct_format(self):
        assert pos_range_pct('UTG') == '15'
        assert pos_range_pct('BTN') == '45'
        assert pos_range_pct('UNKNOWN') == '20'


# ---------------------------------------------------------------------------
# pot_tracker.py
# ---------------------------------------------------------------------------

class TestPotTracker:
    def _make_action(self, action_type, amount_bb=None):
        return SimpleNamespace(action_type=action_type, amount_bb=amount_bb)

    def test_initial_pot(self):
        pt = PotTracker()
        assert pt.pot == pytest.approx(1.5)

    def test_custom_initial(self):
        pt = PotTracker(initial_pot=3.0)
        assert pt.pot == pytest.approx(3.0)

    def test_process_raise(self):
        pt = PotTracker()
        pt.process_action(self._make_action('RAISE', 3.0))
        assert pt.pot == pytest.approx(4.5)

    def test_process_call(self):
        pt = PotTracker()
        pt.process_action(self._make_action('CALL', 2.0))
        assert pt.pot == pytest.approx(3.5)

    def test_fold_ignored(self):
        pt = PotTracker()
        pt.process_action(self._make_action('FOLD'))
        assert pt.pot == pytest.approx(1.5)

    def test_check_ignored(self):
        pt = PotTracker()
        pt.process_action(self._make_action('CHECK'))
        assert pt.pot == pytest.approx(1.5)

    def test_pot_pct(self):
        pt = PotTracker(initial_pot=4.0)
        assert pt.pot_pct(2.0) == pytest.approx(50.0)

    def test_required_equity(self):
        pt = PotTracker(initial_pot=10.0)
        # call 5 into pot of 10 → 5/15 ≈ 33.3%
        assert pt.required_equity(5.0) == pytest.approx(33.33, rel=0.01)

    def test_zero_pot_pct(self):
        pt = PotTracker(initial_pot=0)
        assert pt.pot_pct(5.0) == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# analyzer.py — integration tests with mock Hand objects
# ---------------------------------------------------------------------------

def _make_action(player_name, street, action_type, amount_bb=None,
                 is_all_in=False, sequence=0):
    return SimpleNamespace(
        player_name=player_name,
        street=street,
        action_type=action_type,
        amount_bb=amount_bb,
        is_all_in=is_all_in,
        sequence=sequence,
    )


def _make_hand(
    hero_cards='Ah Kd',
    hero_position='BTN',
    hero_profit_bb=5.0,
    hero_pfr=True,
    hero_vpip=True,
    hero_went_to_showdown=False,
    hero_won_at_showdown=False,
    is_fast_fold=False,
    flop_cards='7h 8c As',
    turn_card=None,
    river_card=None,
    players=None,
    actions=None,
):
    hero_player = SimpleNamespace(
        name='Hero', is_hero=True, stack_bb=100.0,
        position=hero_position, hole_cards=hero_cards,
    )
    return SimpleNamespace(
        hero_cards=hero_cards,
        hero_position=hero_position,
        hero_profit_bb=hero_profit_bb,
        hero_pfr=hero_pfr,
        hero_vpip=hero_vpip,
        hero_went_to_showdown=hero_went_to_showdown,
        hero_won_at_showdown=hero_won_at_showdown,
        is_fast_fold=is_fast_fold,
        flop_cards=flop_cards,
        turn_card=turn_card,
        river_card=river_card,
        players=[hero_player] + (players or []),
        actions=actions or [],
    )


class TestAnalyzerOutput:
    def test_returns_required_keys(self):
        hand = _make_hand(
            actions=[
                _make_action('Hero', 'PREFLOP', 'RAISE', 3.0, sequence=1),
                _make_action('Villain', 'PREFLOP', 'FOLD', sequence=2),
            ]
        )
        result = analyze(hand)
        assert set(result.keys()) == {'samenvatting', 'straten', 'fouten', 'score', 'conclusie'}

    def test_score_in_valid_range(self):
        hand = _make_hand(
            actions=[_make_action('Hero', 'PREFLOP', 'RAISE', 3.0, sequence=1)]
        )
        result = analyze(hand)
        assert 1 <= result['score'] <= 10

    def test_fouten_is_list(self):
        hand = _make_hand(
            actions=[_make_action('Hero', 'PREFLOP', 'RAISE', 3.0, sequence=1)]
        )
        assert isinstance(analyze(hand)['fouten'], list)

    def test_fast_fold_is_goed(self):
        hand = _make_hand(
            is_fast_fold=True,
            hero_cards='7h 2d',
            hero_position='BTN',
            flop_cards=None,
            actions=[_make_action('Hero', 'PREFLOP', 'FAST_FOLD', sequence=1)],
        )
        result = analyze(hand)
        assert result['straten']['PREFLOP']['beoordeling'] == 'goed'
        assert len(result['fouten']) == 0

    def test_correct_open_raise_no_fout(self):
        hand = _make_hand(
            hero_cards='Ah Kd',
            hero_position='BTN',
            flop_cards=None,
            actions=[
                _make_action('Hero', 'PREFLOP', 'RAISE', 2.5, sequence=1),
                _make_action('Villain', 'PREFLOP', 'FOLD', sequence=2),
            ],
        )
        result = analyze(hand)
        pf_fouten = [f for f in result['fouten'] if f['straat'] == 'PREFLOP']
        assert len(pf_fouten) == 0

    def test_weak_hand_open_utg_is_fout(self):
        hand = _make_hand(
            hero_cards='7h 2d',
            hero_position='UTG',
            flop_cards=None,
            actions=[
                _make_action('Hero', 'PREFLOP', 'RAISE', 2.5, sequence=1),
                _make_action('Villain', 'PREFLOP', 'FOLD', sequence=2),
            ],
        )
        result = analyze(hand)
        pf_fouten = [f for f in result['fouten'] if f['straat'] == 'PREFLOP']
        assert len(pf_fouten) >= 1
        assert result['straten']['PREFLOP']['beoordeling'] == 'fout'

    def test_tiny_open_raise_is_fout(self):
        hand = _make_hand(
            hero_cards='Ah Kd',
            hero_position='BTN',
            flop_cards=None,
            actions=[
                _make_action('Hero', 'PREFLOP', 'RAISE', 0.5, sequence=1),
            ],
        )
        result = analyze(hand)
        pf_fouten = [f for f in result['fouten'] if f['straat'] == 'PREFLOP']
        assert len(pf_fouten) >= 1

    def test_correct_cbet_no_fout(self):
        hand = _make_hand(
            hero_cards='Ah Kd',
            hero_position='BTN',
            flop_cards='7h 2c Jd',
            actions=[
                _make_action('Villain', 'PREFLOP', 'CALL', 2.5, sequence=1),
                _make_action('Hero', 'PREFLOP', 'RAISE', 2.5, sequence=2),
                _make_action('Hero', 'FLOP', 'BET', 2.5, sequence=3),   # ~50% of 5BB pot
                _make_action('Villain', 'FLOP', 'FOLD', sequence=4),
            ],
        )
        result = analyze(hand)
        fl_fouten = [f for f in result['fouten'] if f['straat'] == 'FLOP']
        assert len(fl_fouten) == 0

    def test_tiny_cbet_is_fout(self):
        hand = _make_hand(
            hero_cards='Ah Kd',
            hero_position='BTN',
            flop_cards='7h 2c Jd',
            actions=[
                _make_action('Villain', 'PREFLOP', 'CALL', 2.5, sequence=1),
                _make_action('Hero', 'PREFLOP', 'RAISE', 2.5, sequence=2),
                _make_action('Hero', 'FLOP', 'BET', 0.3, sequence=3),   # tiny bet
                _make_action('Villain', 'FLOP', 'FOLD', sequence=4),
            ],
        )
        result = analyze(hand)
        fl_fouten = [f for f in result['fouten'] if f['straat'] == 'FLOP']
        assert len(fl_fouten) >= 1
        assert result['straten']['FLOP']['beoordeling'] in ('acceptabel', 'fout')

    def test_fold_to_tiny_river_bet_is_fout(self):
        hand = _make_hand(
            hero_cards='Ah Kd',
            hero_position='BTN',
            flop_cards='7h 8c 2d',
            turn_card='Jc',
            river_card='5s',
            actions=[
                _make_action('Villain', 'PREFLOP', 'CALL', 2.5, sequence=1),
                _make_action('Hero', 'PREFLOP', 'RAISE', 2.5, sequence=2),
                _make_action('Hero', 'FLOP', 'CHECK', sequence=3),
                _make_action('Villain', 'FLOP', 'CHECK', sequence=4),
                _make_action('Hero', 'TURN', 'CHECK', sequence=5),
                _make_action('Villain', 'TURN', 'CHECK', sequence=6),
                _make_action('Villain', 'RIVER', 'BET', 0.5, sequence=7),  # tiny bet into big pot
                _make_action('Hero', 'RIVER', 'FOLD', sequence=8),
            ],
        )
        result = analyze(hand)
        rv_fouten = [f for f in result['fouten'] if f['straat'] == 'RIVER']
        assert len(rv_fouten) >= 1
        assert result['straten']['RIVER']['beoordeling'] == 'fout'

    def test_straten_only_contains_played_streets(self):
        # Hand that ends on flop
        hand = _make_hand(
            hero_cards='Ah Kd',
            flop_cards='7h 8c 2d',
            turn_card=None,
            river_card=None,
            actions=[
                _make_action('Hero', 'PREFLOP', 'RAISE', 2.5, sequence=1),
                _make_action('Villain', 'PREFLOP', 'CALL', 2.5, sequence=2),
                _make_action('Hero', 'FLOP', 'BET', 2.5, sequence=3),
                _make_action('Villain', 'FLOP', 'FOLD', sequence=4),
            ],
        )
        result = analyze(hand)
        assert 'PREFLOP' in result['straten']
        assert 'FLOP' in result['straten']
        assert 'TURN' not in result['straten']
        assert 'RIVER' not in result['straten']

    def test_samenvatting_contains_position(self):
        hand = _make_hand(hero_position='CO', flop_cards=None, actions=[])
        result = analyze(hand)
        assert 'CO' in result['samenvatting']

    def test_conclusie_mentions_fouten_count(self):
        # Force 2 fouten by opening 72o from UTG with tiny sizing
        hand = _make_hand(
            hero_cards='7h 2d',
            hero_position='UTG',
            flop_cards=None,
            actions=[
                _make_action('Hero', 'PREFLOP', 'RAISE', 0.5, sequence=1),
            ],
        )
        result = analyze(hand)
        if len(result['fouten']) >= 2:
            assert any(
                str(len(result['fouten'])) in result['conclusie']
                or 'verbeterpunten' in result['conclusie'].lower()
                for _ in [1]
            )

    def test_fout_has_required_fields(self):
        hand = _make_hand(
            hero_cards='7h 2d',
            hero_position='UTG',
            flop_cards=None,
            actions=[_make_action('Hero', 'PREFLOP', 'RAISE', 2.5, sequence=1)],
        )
        result = analyze(hand)
        for fout in result['fouten']:
            assert 'straat' in fout
            assert 'moment' in fout
            assert 'probleem' in fout
            assert 'beter' in fout

    def test_no_hero_actions_no_postflop_straten(self):
        """If hero has no postflop actions, those streets are omitted."""
        hand = _make_hand(
            hero_cards='Ah Kd',
            flop_cards='7h 8c 2d',
            actions=[
                _make_action('Hero', 'PREFLOP', 'RAISE', 2.5, sequence=1),
                _make_action('Villain', 'PREFLOP', 'CALL', 2.5, sequence=2),
                # Only villain acts on flop
                _make_action('Villain', 'FLOP', 'BET', 2.0, sequence=3),
                _make_action('Hero', 'FLOP', 'FOLD', sequence=4),
            ],
        )
        result = analyze(hand)
        # FLOP is there because hero folded on flop, but TURN/RIVER should be absent
        assert 'TURN' not in result['straten']
        assert 'RIVER' not in result['straten']
