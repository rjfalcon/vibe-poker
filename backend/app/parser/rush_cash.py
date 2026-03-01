"""Rush & Cash specific stat computation.

Takes a ParsedHand (with raw actions) and fills in all derived boolean
statistics (VPIP, PFR, 3bet, fast-fold, etc.) and hero profit.
"""
from __future__ import annotations

from app.parser.ggpoker_parser import ParsedAction, ParsedHand
from app.stats.positions import compute_positions


def compute_stats(hand: ParsedHand) -> None:
    """Mutate hand in-place: set all derived stat fields and positions."""
    if not hand.hero_name:
        return

    _assign_positions(hand)
    _compute_preflop_stats(hand)
    _compute_postflop_stats(hand)
    _compute_aggression(hand)
    _compute_profit(hand)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _assign_positions(hand: ParsedHand) -> None:
    seat_to_pos = compute_positions(
        seats=[p.seat for p in hand.players],
        button_seat=hand.button_seat,
    )
    for player in hand.players:
        player_pos = seat_to_pos.get(player.seat)
        if player.seat == hand.hero_seat:
            hand.hero_position = player_pos


def _preflop_actions(hand: ParsedHand) -> list[ParsedAction]:
    return [a for a in hand.actions if a.street == "PREFLOP"]


def _hero_actions(hand: ParsedHand, street: str | None = None) -> list[ParsedAction]:
    return [
        a for a in hand.actions
        if a.player_name == hand.hero_name
        and (street is None or a.street == street)
    ]


def _compute_preflop_stats(hand: ParsedHand) -> None:
    preflop = _preflop_actions(hand)

    # is_fast_fold: hero's first preflop action is FAST_FOLD
    hero_preflop = [a for a in preflop if a.player_name == hand.hero_name]
    if hero_preflop and hero_preflop[0].action_type == "FAST_FOLD":
        hand.is_fast_fold = True

    # VPIP: hero CALLed or RAISEd preflop (not blind posting)
    hand.hero_vpip = any(
        a.action_type in ("CALL", "RAISE") for a in hero_preflop
    )

    # PFR: hero RAISEd preflop
    hand.hero_pfr = any(a.action_type == "RAISE" for a in hero_preflop)

    # 3bet opportunity + 3bet made
    raises_seen = 0
    for action in preflop:
        if action.player_name == hand.hero_name:
            if raises_seen == 1:
                # Hero faces exactly one prior raise → 3bet opportunity
                hand.hero_had_3bet_opportunity = True
                if action.action_type == "RAISE":
                    hand.hero_3bet = True
            break
        if action.action_type == "RAISE":
            raises_seen += 1


def _compute_postflop_stats(hand: ParsedHand) -> None:
    # Saw flop: hero was still in the hand when the flop was dealt
    if hand.flop_cards is None:
        return

    folded_preflop = any(
        a.action_type in ("FOLD", "FAST_FOLD")
        for a in hand.actions
        if a.player_name == hand.hero_name and a.street == "PREFLOP"
    )
    hand.hero_saw_flop = not folded_preflop

    # Went to showdown: hand had a showdown section AND hero didn't fold
    hero_folded = any(
        a.action_type in ("FOLD", "FAST_FOLD") for a in _hero_actions(hand)
    )
    hand.hero_went_to_showdown = hand.has_showdown and not hero_folded


def _compute_aggression(hand: ParsedHand) -> None:
    hero = hand.hero_name
    hand.hero_bet_raise_count = sum(
        1 for a in hand.actions
        if a.player_name == hero and a.action_type in ("BET", "RAISE")
    )
    hand.hero_call_count = sum(
        1 for a in hand.actions
        if a.player_name == hero and a.action_type == "CALL"
    )


def _compute_profit(hand: ParsedHand) -> None:
    """Approximate hero profit from pot collections minus money put in."""
    if hand.stakes_bb == 0:
        return

    hero = hand.hero_name

    # Total chips hero invested
    invested = sum(
        a.amount_chips or 0.0
        for a in hand.actions
        if a.player_name == hero and a.action_type in ("CALL", "BET", "RAISE")
    )

    # Add blind postings (not captured as actions)
    # We approximate from the BB/SB amounts based on position
    if hand.hero_position == "BB":
        invested += hand.stakes_bb
    elif hand.hero_position == "SB":
        invested += hand.stakes_sb

    # Chips collected — we need this from the summary, but at parse time
    # we don't have per-player collected info from the summary section yet.
    # The API layer will calculate this from raw data.
    # For now, mark went_to_showdown + won_at_showdown based on cards shown.
    hero_player = next(
        (p for p in hand.players if p.name == hand.hero_name), None
    )
    if hero_player and hero_player.hole_cards and hand.hero_went_to_showdown:
        # Will be refined by the API import layer which reads the SUMMARY
        pass

    # Profit stored temporarily in chips; converted to BB in import layer
    hand.hero_profit_chips = -invested  # net = will be updated by import layer
    hand.hero_profit_bb = hand.hero_profit_chips / hand.stakes_bb
