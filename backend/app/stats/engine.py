"""Statistics engine — computes all player stats from the database."""
from __future__ import annotations

from dataclasses import dataclass, field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.hand import Hand
from app.models.action import Action


@dataclass
class OverviewStats:
    total_hands: int = 0
    hands_played_out: int = 0    # hero did NOT fast-fold
    hands_fast_folded: int = 0
    fast_fold_pct: float = 0.0

    vpip: float = 0.0
    pfr: float = 0.0
    three_bet_pct: float = 0.0
    af: float = 0.0               # Aggression Factor (all streets)
    wtsd: float = 0.0             # Went To ShowDown %
    wsd: float = 0.0              # Won money at ShowDown %
    bb_per_100: float = 0.0
    total_profit_bb: float = 0.0
    rake_bb: float = 0.0


@dataclass
class PositionStats:
    position: str = ""
    hands: int = 0
    vpip: float = 0.0
    pfr: float = 0.0
    three_bet_pct: float = 0.0
    bb_per_100: float = 0.0
    total_profit_bb: float = 0.0


class StatsEngine:
    def __init__(self, db: Session):
        self._db = db

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def overview(self, session_id: str | None = None) -> OverviewStats:
        hands = self._hand_query(session_id).all()
        return self._compute_overview(hands)

    def by_position(self, session_id: str | None = None) -> list[PositionStats]:
        hands = self._hand_query(session_id).all()
        positions: dict[str, list[Hand]] = {}
        for h in hands:
            pos = h.hero_position or "UNKNOWN"
            positions.setdefault(pos, []).append(h)

        result = []
        for pos, pos_hands in positions.items():
            stats = self._compute_overview(pos_hands)
            result.append(
                PositionStats(
                    position=pos,
                    hands=stats.total_hands,
                    vpip=stats.vpip,
                    pfr=stats.pfr,
                    three_bet_pct=stats.three_bet_pct,
                    bb_per_100=stats.bb_per_100,
                    total_profit_bb=stats.total_profit_bb,
                )
            )

        _POSITION_ORDER = ["UTG", "UTG+1", "UTG+2", "MP", "HJ", "CO", "BTN", "SB", "BB"]
        result.sort(key=lambda s: _POSITION_ORDER.index(s.position)
                    if s.position in _POSITION_ORDER else 99)
        return result

    # ------------------------------------------------------------------
    # Core computation
    # ------------------------------------------------------------------

    def _compute_overview(self, hands: list[Hand]) -> OverviewStats:
        s = OverviewStats()
        if not hands:
            return s

        s.total_hands = len(hands)
        s.hands_fast_folded = sum(1 for h in hands if h.is_fast_fold)
        s.hands_played_out = s.total_hands - s.hands_fast_folded
        s.fast_fold_pct = _pct(s.hands_fast_folded, s.total_hands)

        s.vpip = _pct(sum(1 for h in hands if h.hero_vpip), s.total_hands)
        s.pfr = _pct(sum(1 for h in hands if h.hero_pfr), s.total_hands)

        three_bet_opps = [h for h in hands if h.hero_had_3bet_opportunity]
        s.three_bet_pct = _pct(
            sum(1 for h in three_bet_opps if h.hero_3bet), len(three_bet_opps)
        )

        total_bets_raises = sum(h.hero_bet_raise_count for h in hands)
        total_calls = sum(h.hero_call_count for h in hands)
        s.af = round(total_bets_raises / total_calls, 2) if total_calls else float(total_bets_raises)

        flop_hands = [h for h in hands if h.hero_saw_flop]
        s.wtsd = _pct(sum(1 for h in flop_hands if h.hero_went_to_showdown), len(flop_hands))

        sd_hands = [h for h in hands if h.hero_went_to_showdown]
        s.wsd = _pct(sum(1 for h in sd_hands if h.hero_won_at_showdown), len(sd_hands))

        s.total_profit_bb = sum(h.hero_profit_bb for h in hands)
        s.bb_per_100 = round((s.total_profit_bb / s.total_hands) * 100, 2)
        s.rake_bb = sum(h.rake_bb for h in hands)

        return s

    def _hand_query(self, session_id: str | None):
        q = self._db.query(Hand)
        if session_id:
            q = q.filter(Hand.session_id == session_id)
        return q


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 1)
