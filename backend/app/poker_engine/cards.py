"""Card parsing and hand classification utilities."""
from __future__ import annotations

RANKS: dict[str, int] = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14,
}
_RANK_CHAR = {v: k for k, v in RANKS.items()}

Card = tuple[int, str]  # (rank_int, suit)


def parse_card(s: str) -> Card:
    """Parse 'Ah' → (14, 'h')."""
    s = s.strip()
    rank = RANKS.get(s[0].upper(), 0)
    suit = s[1].lower() if len(s) > 1 else '?'
    return (rank, suit)


def parse_hand(s: str | None) -> list[Card] | None:
    """Parse 'Ah Kd' → [(14, 'h'), (13, 'd')]. Returns None on failure."""
    if not s:
        return None
    parts = s.strip().split()
    if len(parts) < 2:
        return None
    return [parse_card(p) for p in parts[:2]]


def hand_key(c1: Card, c2: Card) -> str:
    """Return normalized hand key: 'AKs', 'AKo', 'AA', etc."""
    r1, s1 = c1
    r2, s2 = c2
    if r1 < r2:
        r1, r2, s1, s2 = r2, r1, s2, s1
    rc1 = _RANK_CHAR[r1]
    rc2 = _RANK_CHAR[r2]
    if r1 == r2:
        return f"{rc1}{rc2}"
    suffix = 's' if s1 == s2 else 'o'
    return f"{rc1}{rc2}{suffix}"


def hand_category(c1: Card, c2: Card) -> str:
    """Classify hand as 'premium', 'strong', 'speculative', or 'weak'."""
    r1, s1 = c1
    r2, s2 = c2
    if r1 < r2:
        r1, r2, s1, s2 = r2, r1, s2, s1
    suited = s1 == s2

    # Pocket pairs
    if r1 == r2:
        if r1 >= 11:  # JJ+
            return 'premium'
        if r1 >= 8:   # 88-TT
            return 'strong'
        return 'speculative'

    # Ace-x
    if r1 == 14:
        if r2 == 13:               return 'premium'   # AK
        if r2 >= 11 and suited:    return 'strong'    # AQs, AJs
        if r2 >= 10:               return 'strong'    # ATs, AQo, AJo, ATo
        if suited:                 return 'speculative'
        return 'weak'

    # King-x
    if r1 == 13:
        if r2 >= 12:               return 'strong'    # KQ
        if r2 >= 10 and suited:    return 'speculative'  # KTs, KJs
        if r2 >= 8 and suited:     return 'speculative'
        return 'weak'

    # Queen-x and lower suited connectors
    if suited:
        if r1 == 12 and r2 >= 10:  return 'speculative'  # QTs+
        if r1 == 11 and r2 >= 9:   return 'speculative'  # J9s+
        if abs(r1 - r2) <= 2 and r2 >= 5:
            return 'speculative'   # connected/one-gap suited 5+

    return 'weak'


def board_texture(card_strings: list[str]) -> dict:
    """Analyze board texture from list of card strings like ['7h', '8c', 'As']."""
    if not card_strings:
        return {
            'flush_draw': False,
            'straight_draw': False,
            'paired': False,
            'high_card': 0,
            'wet': False,
        }

    cards = [parse_card(c) for c in card_strings if c]
    ranks = [c[0] for c in cards]
    suits = [c[1] for c in cards]

    # Flush draw: 2+ same suit on board
    suit_counts: dict[str, int] = {}
    for s in suits:
        suit_counts[s] = suit_counts.get(s, 0) + 1
    flush_draw = max(suit_counts.values()) >= 2

    # Straight draw: any two cards within 4 of each other
    sorted_ranks = sorted(set(ranks))
    straight_draw = any(
        sorted_ranks[j] - sorted_ranks[i] <= 4
        for i in range(len(sorted_ranks))
        for j in range(i + 1, len(sorted_ranks))
    )

    paired = len(ranks) != len(set(ranks))
    high_card = max(ranks) if ranks else 0
    wet = flush_draw or straight_draw

    return {
        'flush_draw': flush_draw,
        'straight_draw': straight_draw,
        'paired': paired,
        'high_card': high_card,
        'wet': wet,
    }
