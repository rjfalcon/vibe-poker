"""Split a multi-hand .txt export into individual hand text blocks."""
import re

_HAND_DELIMITER = re.compile(r"(?=Poker Hand #)")


def split_hands(text: str) -> list[str]:
    """Return a list of individual hand text blocks from a GGPoker export file."""
    blocks = _HAND_DELIMITER.split(text)
    return [b.strip() for b in blocks if b.strip().startswith("Poker Hand #")]
