"""Simple pot tracker for bet-sizing analysis."""
from __future__ import annotations

_BETTING_ACTIONS = frozenset({'CALL', 'BET', 'RAISE', 'ALL_IN'})


class PotTracker:
    """Tracks the running pot in big blinds across all streets.

    NOTE: amount_bb for RAISE is the *total* bet amount; for CALL it is the
    incremental amount called. Summing all contributions gives a close
    approximation of the pot (slight overcount when raises are re-raised).
    """

    def __init__(self, initial_pot: float = 1.5) -> None:
        # Start with SB (0.5BB) + BB (1BB) already in the pot
        self._pot = initial_pot

    def process_action(self, action) -> None:
        if action.amount_bb and action.action_type in _BETTING_ACTIONS:
            self._pot += action.amount_bb

    @property
    def pot(self) -> float:
        return self._pot

    def pot_pct(self, bet_amount: float) -> float:
        """Return bet_amount as percentage of current pot (0–∞)."""
        if self._pot <= 0:
            return 100.0
        return (bet_amount / self._pot) * 100

    def required_equity(self, call_amount: float) -> float:
        """Return minimum equity % needed to call profitably."""
        total = self._pot + call_amount
        if total <= 0:
            return 0.0
        return (call_amount / total) * 100
