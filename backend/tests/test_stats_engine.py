"""Tests for the stats engine (position calculation, overview stats)."""
import pytest
from app.stats.positions import compute_positions


class TestPositionComputation:
    def test_six_max_button_at_first_seat(self):
        seats = [1, 2, 3, 4, 5, 6]
        result = compute_positions(seats, button_seat=1)
        assert result[1] == "BTN"
        assert result[2] == "SB"
        assert result[3] == "BB"
        assert result[4] == "UTG"
        assert result[5] == "HJ"
        assert result[6] == "CO"

    def test_six_max_button_in_middle(self):
        seats = [1, 2, 3, 4, 5, 6]
        result = compute_positions(seats, button_seat=4)
        assert result[4] == "BTN"
        assert result[5] == "SB"
        assert result[6] == "BB"
        assert result[1] == "UTG"
        assert result[2] == "HJ"
        assert result[3] == "CO"

    def test_six_max_button_wraps_around(self):
        seats = [1, 2, 3, 4, 5, 6]
        result = compute_positions(seats, button_seat=6)
        assert result[6] == "BTN"
        assert result[1] == "SB"
        assert result[2] == "BB"
        assert result[3] == "UTG"
        assert result[4] == "HJ"
        assert result[5] == "CO"

    def test_five_max_positions(self):
        seats = [1, 2, 3, 4, 5]
        result = compute_positions(seats, button_seat=3)
        assert result[3] == "BTN"
        assert result[4] == "SB"
        assert result[5] == "BB"
        assert result[1] == "UTG"
        assert result[2] == "CO"

    def test_heads_up_positions(self):
        seats = [2, 5]
        result = compute_positions(seats, button_seat=2)
        assert result[2] == "BTN"
        assert result[5] == "BB"

    def test_empty_seats_returns_empty(self):
        result = compute_positions([], button_seat=1)
        assert result == {}

    def test_non_sequential_seat_numbers(self):
        """GGPoker can have gaps in seat numbers when not all seats are taken."""
        seats = [1, 3, 5]
        result = compute_positions(seats, button_seat=3)
        assert result[3] == "BTN"
        assert result[5] == "SB"
        assert result[1] == "BB"

    def test_all_nine_positions(self):
        seats = list(range(1, 10))
        result = compute_positions(seats, button_seat=1)
        assert result[1] == "BTN"
        assert len(result) == 9
        # All values must be unique
        assert len(set(result.values())) == 9
