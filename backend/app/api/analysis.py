"""AI hand analysis via Claude."""
from __future__ import annotations

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.database import get_db
from app.models.hand import Hand

router = APIRouter(prefix="/hands", tags=["analysis"])

_SYSTEM_PROMPT = """Je bent een elite poker coach met de kennis van een GTO solver en \
tientallen jaren ervaring in cash games op het hoogste niveau.

Analyseer de gegeven Rush & Cash hand vanuit het perspectief van Hero. \
Acties gemarkeerd met [HERO] zijn van de speler die je analyseert. \
Geef je analyse volledig in het Nederlands.

Geef je antwoord als geldig JSON met exact dit formaat:
{
  "samenvatting": "1-2 zinnen over de hand en de kernbeslissingen",
  "straten": {
    "PREFLOP": {"beoordeling": "goed", "uitleg": "analyse van de preflop acties"},
    "FLOP":    {"beoordeling": "acceptabel", "uitleg": "..."},
    "TURN":    {"beoordeling": "fout", "uitleg": "..."},
    "RIVER":   {"beoordeling": "goed", "uitleg": "..."}
  },
  "fouten": [
    {
      "straat": "FLOP",
      "moment": "Hero bet 5BB in pot van 8BB",
      "probleem": "Sizing te groot: lost de sterke handen in de range van Villain uit",
      "beter": "Gebruik een kleinere sizing van 33-40% pot om brede range te behouden"
    }
  ],
  "score": 7,
  "conclusie": "1-2 zinnen afsluiting met de belangrijkste les uit deze hand"
}

Regels:
- Laat straten die niet bereikt zijn weg uit "straten"
- Als er geen fouten zijn: lege array [] voor "fouten"
- score: 1-10 (10=perfect, 7=goede speler met kleine fout, 5=gemiddeld, 3=ernstige fout)
- beoordeling moet exact "goed", "acceptabel" of "fout" zijn
- Wees concreet: noem pot odds, sizing percentages, equity, hand-ranges
- Geef ALLEEN het JSON object terug, geen extra tekst"""


@router.post("/{hand_id}/analyze")
def analyze_hand(hand_id: str, db: Session = Depends(get_db)):
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="AI analyse niet beschikbaar (ANTHROPIC_API_KEY niet geconfigureerd)",
        )

    hand = (
        db.query(Hand)
        .options(selectinload(Hand.players), selectinload(Hand.actions))
        .filter(Hand.id == hand_id)
        .first()
    )
    if not hand:
        raise HTTPException(status_code=404, detail="Hand not found")

    hand_text = _build_hand_text(hand)

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": hand_text}],
        )
        raw = response.content[0].text.strip()
        # Strip optional markdown code fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"Ongeldig AI-antwoord: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI analyse mislukt: {e}")


# ---------------------------------------------------------------------------
# Hand text builder
# ---------------------------------------------------------------------------

def _build_hand_text(hand: Hand) -> str:
    hero = next((p for p in hand.players if p.is_hero), None)
    lines: list[str] = []

    lines.append(f"Rush & Cash NLH ${hand.stakes_sb:.2f}/${hand.stakes_bb:.2f} (6-max)")
    lines.append(f"Hand: {hand.ggpoker_hand_id}")
    lines.append("")

    lines.append("SPELERS (positie — naam — stack — kaarten):")
    pos_order = ["UTG", "UTG+1", "MP", "HJ", "CO", "BTN", "SB", "BB"]
    players_sorted = sorted(
        hand.players,
        key=lambda p: pos_order.index(p.position) if p.position in pos_order else 99,
    )
    for p in players_sorted:
        hero_tag = " [HERO]" if p.is_hero else ""
        cards = f" | kaarten: {p.hole_cards}" if p.hole_cards else ""
        pos = p.position or "?"
        lines.append(f"  {pos} — {p.name}: {p.stack_bb:.1f}BB{cards}{hero_tag}")
    lines.append("")

    board_so_far: list[str] = []
    for street in ("PREFLOP", "FLOP", "TURN", "RIVER"):
        actions = sorted(
            [a for a in hand.actions if a.street == street],
            key=lambda a: a.sequence,
        )
        if not actions and street != "PREFLOP":
            continue

        if street == "FLOP" and hand.flop_cards:
            board_so_far += hand.flop_cards.split()
            lines.append(f"FLOP [{hand.flop_cards}]:")
        elif street == "TURN" and hand.turn_card:
            board_so_far.append(hand.turn_card)
            lines.append(f"TURN [{' '.join(board_so_far)}]:")
        elif street == "RIVER" and hand.river_card:
            board_so_far.append(hand.river_card)
            lines.append(f"RIVER [{' '.join(board_so_far)}]:")
        else:
            lines.append(f"{street}:")

        for a in actions:
            is_hero = a.player_name == (hero.name if hero else "")
            tag = " [HERO]" if is_hero else ""
            amount = f" {a.amount_bb:.1f}BB" if a.amount_bb is not None else ""
            allin = " (ALL-IN)" if a.is_all_in else ""
            lines.append(f"  {a.player_name}{tag}: {a.action_type}{amount}{allin}")
        lines.append("")

    lines.append("RESULTAAT:")
    lines.append(f"  Hero profit: {hand.hero_profit_bb:+.1f}BB")
    if hand.hero_went_to_showdown:
        uitslag = "gewonnen" if hand.hero_won_at_showdown else "verloren"
        lines.append(f"  Showdown: {uitslag}")
    if hand.is_fast_fold:
        lines.append("  (Fast Fold — Hero foldde vóór de actie aan hem was)")

    return "\n".join(lines)
