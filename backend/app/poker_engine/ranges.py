"""GTO 6-max preflop opening ranges."""
from __future__ import annotations
from app.poker_engine.cards import Card

# Approximate RFI (Raise First In) percentages per position:
# UTG ~15%, HJ ~20%, CO ~27%, BTN ~45%, SB ~35%

_POS_RANGE_PCT = {
    'UTG': '15', 'UTG+1': '17', 'MP': '17',
    'HJ': '20', 'CO': '27', 'BTN': '45',
    'SB': '35', 'BB': '50',
}


def pos_range_pct(position: str) -> str:
    return _POS_RANGE_PCT.get(position, '20')


def hand_in_range(c1: Card, c2: Card, position: str) -> bool:
    """Return True if this hand is in a standard GTO RFI range for the position."""
    r1, s1 = c1
    r2, s2 = c2
    if r1 < r2:
        r1, r2, s1, s2 = r2, r1, s2, s1
    suited = s1 == s2
    pair = r1 == r2

    # Normalize position aliases
    pos = position.upper().replace('+1', '+1')
    if pos in ('UTG', 'UTG+1', 'MP'):
        # Tight: pairs 99+, premium/strong suited, AJo+, KQo
        if pair:            return r1 >= 9
        if suited:
            if r1 == 14:     return r2 >= 9   # A9s+
            if r1 == 13:     return r2 >= 11  # KJs+
            if r1 == 12:     return r2 == 11  # QJs
            if r1 == 11:     return r2 == 10  # JTs
            return False
        else:
            if r1 == 14:     return r2 >= 11  # AJo+
            if r1 == 13:     return r2 == 12  # KQo
            return False

    if pos == 'HJ':
        if pair:             return r1 >= 8   # 88+
        if suited:
            if r1 == 14:     return r2 >= 7   # A7s+
            if r1 == 13:     return r2 >= 10  # KTs+
            if r1 == 12:     return r2 >= 10  # QTs+
            if r1 == 11:     return r2 >= 9   # J9s+
            if r1 == 10:     return r2 == 9   # T9s
            return False
        else:
            if r1 == 14:     return r2 >= 10  # ATo+
            if r1 == 13:     return r2 >= 11  # KJo+
            if r1 == 12:     return r2 == 11  # QJo
            return False

    if pos == 'CO':
        if pair:             return r1 >= 6   # 66+
        if suited:
            if r1 == 14:     return True      # All Ax suited
            if r1 == 13:     return r2 >= 9   # K9s+
            if r1 == 12:     return r2 >= 9   # Q9s+
            if r1 == 11:     return r2 >= 8   # J8s+
            if r1 == 10:     return r2 >= 8   # T8s+
            if r1 == 9:      return r2 >= 7   # 97s+
            if r1 == 8:      return r2 == 7   # 87s
            if r1 == 7:      return r2 == 6   # 76s
            return False
        else:
            if r1 == 14:     return r2 >= 9   # A9o+
            if r1 == 13:     return r2 >= 10  # KTo+
            if r1 == 12:     return r2 >= 10  # QTo+
            if r1 == 11:     return r2 == 10  # JTo
            return False

    if pos == 'BTN':
        if pair:             return True      # All pairs
        if suited:
            if r1 == 14:     return True      # All Ax suited
            if r1 == 13:     return r2 >= 7   # K7s+
            if r1 == 12:     return r2 >= 7   # Q7s+
            if r1 == 11:     return r2 >= 6   # J6s+
            if r1 == 10:     return r2 >= 6   # T6s+
            if r1 == 9:      return r2 >= 6   # 96s+
            if r1 == 8:      return r2 >= 6   # 86s+
            if r1 == 7:      return r2 >= 5   # 75s+
            if r1 == 6:      return r2 == 5   # 65s
            return False
        else:
            if r1 == 14:     return r2 >= 7   # A7o+
            if r1 == 13:     return r2 >= 9   # K9o+
            if r1 == 12:     return r2 >= 9   # Q9o+
            if r1 == 11:     return r2 >= 9   # J9o+
            if r1 == 10:     return r2 == 9   # T9o
            return False

    if pos == 'SB':
        if pair:             return r1 >= 5   # 55+
        if suited:
            if r1 == 14:     return r2 >= 3   # A3s+
            if r1 == 13:     return r2 >= 9   # K9s+
            if r1 == 12:     return r2 >= 9   # Q9s+
            if r1 == 11:     return r2 >= 8   # J8s+
            if r1 == 10:     return r2 >= 8   # T8s+
            if r1 == 9:      return r2 >= 7   # 97s+
            if r1 == 8:      return r2 == 7   # 87s
            return False
        else:
            if r1 == 14:     return r2 >= 9   # A9o+
            if r1 == 13:     return r2 >= 10  # KTo+
            if r1 == 12:     return r2 == 11  # QJo
            return False

    if pos == 'BB':
        # BB defends wide vs most opens; very hard to say "outside range"
        # Only flag truly unplayable hands
        if pair:             return True
        if suited:           return r1 >= 5 or r2 >= 5
        if r1 == 14:         return r2 >= 5
        return r1 >= 9 and r2 >= 7

    # Unknown position — don't flag
    return True
