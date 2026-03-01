from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class SessionOut(BaseModel):
    id: str
    filename: str
    imported_at: datetime
    hero_name: Optional[str]
    hand_count: int

    model_config = {"from_attributes": True}


class BulkImportOut(BaseModel):
    total_hands: int
    session_count: int
    sessions: List[SessionOut]


class PlayerOut(BaseModel):
    seat: int
    name: str
    stack_bb: float
    position: Optional[str]
    is_hero: bool
    hole_cards: Optional[str]
    profit_bb: float

    model_config = {"from_attributes": True}


class ActionOut(BaseModel):
    player_name: str
    street: str
    sequence: int
    action_type: str
    amount_bb: Optional[float]
    is_all_in: bool

    model_config = {"from_attributes": True}


class HandSummary(BaseModel):
    id: str
    ggpoker_hand_id: str
    played_at: datetime
    stakes_bb: float
    table_name: str
    hero_position: Optional[str]
    hero_cards: Optional[str]
    is_fast_fold: bool
    hero_vpip: bool
    hero_pfr: bool
    hero_profit_bb: float
    flop_cards: Optional[str]
    run_it_twice: bool

    model_config = {"from_attributes": True}


class HandDetail(HandSummary):
    hero_went_to_showdown: bool
    hero_won_at_showdown: bool
    hero_had_3bet_opportunity: bool
    hero_3bet: bool
    turn_card: Optional[str]
    river_card: Optional[str]
    rake_bb: float
    players: List[PlayerOut]
    actions: List[ActionOut]
