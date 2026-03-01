"""Compute positional labels for each seat in a hand.

Positions (clockwise from button):
  2-max:  BTN, BB
  3-max:  BTN, SB, BB
  4-max:  BTN, SB, BB, UTG
  5-max:  BTN, SB, BB, UTG, CO
  6-max:  BTN, SB, BB, UTG, HJ, CO
  7-max:  BTN, SB, BB, UTG, UTG+1, HJ, CO
  8-max:  BTN, SB, BB, UTG, UTG+1, UTG+2, HJ, CO
  9-max:  BTN, SB, BB, UTG, UTG+1, UTG+2, MP, HJ, CO
"""

_POSITIONS_BY_COUNT: dict[int, list[str]] = {
    2: ["BTN", "BB"],
    3: ["BTN", "SB", "BB"],
    4: ["BTN", "SB", "BB", "UTG"],
    5: ["BTN", "SB", "BB", "UTG", "CO"],
    6: ["BTN", "SB", "BB", "UTG", "HJ", "CO"],
    7: ["BTN", "SB", "BB", "UTG", "UTG+1", "HJ", "CO"],
    8: ["BTN", "SB", "BB", "UTG", "UTG+1", "UTG+2", "HJ", "CO"],
    9: ["BTN", "SB", "BB", "UTG", "UTG+1", "UTG+2", "MP", "HJ", "CO"],
}


def compute_positions(seats: list[int], button_seat: int) -> dict[int, str]:
    """Return a mapping {seat_number: position_label} for the given hand.

    Seats must be the list of occupied seat numbers (1-9).
    """
    if not seats:
        return {}

    # Sort seats numerically and find the index of the button seat
    sorted_seats = sorted(seats)
    n = len(sorted_seats)

    try:
        btn_idx = sorted_seats.index(button_seat)
    except ValueError:
        # Button seat not in occupied seats — fallback
        btn_idx = 0

    labels = _POSITIONS_BY_COUNT.get(n, _fallback_labels(n))

    # Rotate seats so button is first
    rotated = sorted_seats[btn_idx:] + sorted_seats[:btn_idx]

    return {seat: labels[i] for i, seat in enumerate(rotated)}


def _fallback_labels(n: int) -> list[str]:
    """Generate generic labels for unusual table sizes."""
    base = ["BTN", "SB", "BB"]
    middle = [f"MP{i}" for i in range(1, n - 3)]
    return base + middle + ["CO"] if n > 3 else base[:n]
