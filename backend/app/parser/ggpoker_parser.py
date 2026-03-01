"""GGPoker hand history parser.

Handles NLH cash game format including Rush & Cash fast-fold variant.
Produces ParsedHand dataclasses that are later persisted to the database.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from dateutil import parser as dateparser


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ParsedAction:
    player_name: str
    street: str           # PREFLOP | FLOP | TURN | RIVER
    action_type: str      # FOLD | FAST_FOLD | CHECK | CALL | BET | RAISE
    amount_chips: float | None
    is_all_in: bool
    sequence: int         # global order across entire hand


@dataclass
class ParsedPlayer:
    seat: int
    name: str
    stack_chips: float
    hole_cards: str | None = None


@dataclass
class ParsedHand:
    ggpoker_hand_id: str
    table_name: str
    game_type: str
    stakes_sb: float
    stakes_bb: float
    played_at: datetime
    button_seat: int
    num_players: int

    players: list[ParsedPlayer] = field(default_factory=list)
    actions: list[ParsedAction] = field(default_factory=list)

    hero_name: str | None = None
    hero_seat: int | None = None
    hero_cards: str | None = None
    hero_position: str | None = None

    flop_cards: str | None = None
    turn_card: str | None = None
    river_card: str | None = None
    run_it_twice: bool = False
    has_showdown: bool = False   # True when *** SHOW DOWN *** section was present

    pot_total_chips: float = 0.0
    rake_chips: float = 0.0

    # Derived stats — populated by rush_cash.compute_stats()
    is_fast_fold: bool = False
    hero_vpip: bool = False
    hero_pfr: bool = False
    hero_had_3bet_opportunity: bool = False
    hero_3bet: bool = False
    hero_saw_flop: bool = False
    hero_went_to_showdown: bool = False
    hero_won_at_showdown: bool = False
    hero_bet_raise_count: int = 0
    hero_call_count: int = 0
    hero_profit_chips: float = 0.0
    hero_profit_bb: float = 0.0


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

_HEADER_RE = re.compile(
    r"Poker Hand #([\w]+): (.+?) \(\$([0-9.]+)/\$([0-9.]+)\) - "
    r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})"
)
_TABLE_RE = re.compile(
    r"Table '(.+?)' \d+-Max.*?Seat #(\d+) is the button"
)
_SEAT_RE = re.compile(
    r"Seat (\d+): (.+?) \(\$([0-9.]+) in chips\)"
)
_DEALT_RE = re.compile(r"Dealt to (.+?) \[(.+?)\]")
_SECTION_RE = re.compile(r"^\*{3}\s*(.+?)\s*\*{3}")
_FLOP_RE = re.compile(r"\*\*\* FLOP \*\*\* \[(.+?)\]")
_TURN_RE = re.compile(r"\*\*\* TURN \*\*\* \[.+?\] \[(.+?)\]")
_RIVER_RE = re.compile(r"\*\*\* RIVER \*\*\* \[.+?\] \[(.+?)\]")
_POT_RE = re.compile(r"Total pot \$([0-9.]+) \| Rake \$([0-9.]+)")
_COLLECTED_RE = re.compile(
    r"(.+?) collected \$([0-9.]+) from (?:main |side )?pot"
)
_UNCALLED_RE = re.compile(r"Uncalled bet \(\$([0-9.]+)\) returned to (.+)")
_BLIND_RE = re.compile(
    r"^(.+?): posts (?:small blind|big blind|ante) \$([0-9.]+)"
)
_SHOWS_RE = re.compile(r"^(.+?): shows \[(.+?)\]")

# Action line: "PlayerName: action ..."
_ACTION_LINE_RE = re.compile(r"^(.+?): (.+)$")


# ---------------------------------------------------------------------------
# Parser class
# ---------------------------------------------------------------------------

class GGPokerParser:
    """Parse a single GGPoker hand history text block into a ParsedHand."""

    def parse(self, text: str) -> ParsedHand | None:
        lines = [ln.rstrip() for ln in text.splitlines()]
        if not lines:
            return None

        hand = self._parse_header(lines[0])
        if hand is None:
            return None

        state = "SEATS"
        seq = 0       # global action sequence counter
        street = "PREFLOP"

        for line in lines[1:]:
            if not line:
                continue

            # --- Section markers ---
            section_match = _SECTION_RE.match(line)
            if section_match:
                section = section_match.group(1).upper()
                if "HOLE CARDS" in section:
                    state = "PREFLOP"
                    street = "PREFLOP"
                elif "FLOP" in section:
                    state = "FLOP"
                    street = "FLOP"
                    m = _FLOP_RE.match(line)
                    if m:
                        hand.flop_cards = m.group(1)
                elif "TURN" in section:
                    state = "TURN"
                    street = "TURN"
                    m = _TURN_RE.match(line)
                    if m:
                        hand.turn_card = m.group(1)
                elif "RIVER" in section:
                    state = "RIVER"
                    street = "RIVER"
                    m = _RIVER_RE.match(line)
                    if m:
                        hand.river_card = m.group(1)
                elif "SHOW" in section:
                    state = "SHOWDOWN"
                    hand.has_showdown = True
                elif "RUN IT TWICE" in section:
                    hand.run_it_twice = True
                elif "SUMMARY" in section:
                    state = "SUMMARY"
                continue

            # --- State-specific parsing ---
            if state == "SEATS":
                self._parse_seat_line(hand, line)

            elif state in ("PREFLOP", "FLOP", "TURN", "RIVER"):
                dealt = _DEALT_RE.match(line)
                if dealt:
                    hand.hero_name = dealt.group(1)
                    hand.hero_cards = dealt.group(2)
                    # Find hero seat
                    for p in hand.players:
                        if p.name == hand.hero_name:
                            hand.hero_seat = p.seat
                            p.hole_cards = hand.hero_cards
                            break
                    continue

                action = self._parse_action_line(line, street, seq)
                if action:
                    hand.actions.append(action)
                    seq += 1

            elif state == "SHOWDOWN":
                m = _SHOWS_RE.match(line)
                if m:
                    name, cards = m.group(1), m.group(2)
                    for p in hand.players:
                        if p.name == name:
                            p.hole_cards = cards
                            break

            elif state == "SUMMARY":
                pot_m = _POT_RE.match(line)
                if pot_m:
                    hand.pot_total_chips = float(pot_m.group(1))
                    hand.rake_chips = float(pot_m.group(2))

        return hand

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_header(self, line: str) -> ParsedHand | None:
        m = _HEADER_RE.match(line)
        if not m:
            return None
        return ParsedHand(
            ggpoker_hand_id=m.group(1),
            game_type=self._normalize_game_type(m.group(2)),
            stakes_sb=float(m.group(3)),
            stakes_bb=float(m.group(4)),
            played_at=dateparser.parse(m.group(5)),
            table_name="",
            button_seat=0,
            num_players=0,
        )

    def _parse_seat_line(self, hand: ParsedHand, line: str) -> None:
        # Table line
        t = _TABLE_RE.match(line)
        if t:
            hand.table_name = t.group(1)
            hand.button_seat = int(t.group(2))
            return

        # Seat line
        s = _SEAT_RE.match(line)
        if s:
            hand.players.append(
                ParsedPlayer(
                    seat=int(s.group(1)),
                    name=s.group(2),
                    stack_chips=float(s.group(3)),
                )
            )
            hand.num_players = len(hand.players)
            return

    def _parse_action_line(
        self, line: str, street: str, seq: int
    ) -> ParsedAction | None:
        # Skip non-action lines
        m = _ACTION_LINE_RE.match(line)
        if not m:
            return None

        player, rest = m.group(1), m.group(2)

        # Skip blind postings (not betting actions for stats)
        if _BLIND_RE.match(line):
            return None

        # Skip "collected" and "Uncalled" — handled separately
        if "collected" in rest or rest.startswith("Uncalled"):
            return None

        return self._classify_action(player, rest, street, seq)

    def _classify_action(
        self, player: str, rest: str, street: str, seq: int
    ) -> ParsedAction | None:
        rest_lower = rest.lower()
        is_fast_fold = "[fast fold]" in rest_lower
        is_all_in = "all-in" in rest_lower

        if rest_lower.startswith("folds"):
            return ParsedAction(
                player_name=player,
                street=street,
                action_type="FAST_FOLD" if is_fast_fold else "FOLD",
                amount_chips=None,
                is_all_in=False,
                sequence=seq,
            )

        if rest_lower.startswith("checks"):
            return ParsedAction(
                player_name=player,
                street=street,
                action_type="CHECK",
                amount_chips=None,
                is_all_in=False,
                sequence=seq,
            )

        if rest_lower.startswith("calls"):
            amount = self._extract_first_amount(rest)
            return ParsedAction(
                player_name=player,
                street=street,
                action_type="CALL",
                amount_chips=amount,
                is_all_in=is_all_in,
                sequence=seq,
            )

        if rest_lower.startswith("bets"):
            amount = self._extract_first_amount(rest)
            return ParsedAction(
                player_name=player,
                street=street,
                action_type="BET",
                amount_chips=amount,
                is_all_in=is_all_in,
                sequence=seq,
            )

        if rest_lower.startswith("raises"):
            # "raises $X.XX to $Y.YY" — total bet is the "to" amount
            to_match = re.search(r"to \$([0-9.]+)", rest)
            amount = float(to_match.group(1)) if to_match else self._extract_first_amount(rest)
            return ParsedAction(
                player_name=player,
                street=street,
                action_type="RAISE",
                amount_chips=amount,
                is_all_in=is_all_in,
                sequence=seq,
            )

        return None

    @staticmethod
    def _extract_first_amount(text: str) -> float | None:
        m = re.search(r"\$([0-9.]+)", text)
        return float(m.group(1)) if m else None

    @staticmethod
    def _normalize_game_type(raw: str) -> str:
        raw_upper = raw.upper()
        if "HOLD'EM" in raw_upper or "HOLDEM" in raw_upper:
            return "NLH"
        if "OMAHA" in raw_upper:
            return "PLO"
        return raw.strip()
