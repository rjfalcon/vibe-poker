from datetime import datetime
from pydantic import BaseModel


class OverviewStatsOut(BaseModel):
    total_hands: int
    hands_played_out: int
    hands_fast_folded: int
    fast_fold_pct: float
    vpip: float
    pfr: float
    three_bet_pct: float
    af: float
    wtsd: float
    wsd: float
    bb_per_100: float
    total_profit_bb: float
    rake_bb: float


class PositionStatsOut(BaseModel):
    position: str
    hands: int
    vpip: float
    pfr: float
    three_bet_pct: float
    bb_per_100: float
    total_profit_bb: float


class TimelinePointOut(BaseModel):
    index: int
    played_at: datetime
    cumulative_bb: float
    bb_per_100: float
