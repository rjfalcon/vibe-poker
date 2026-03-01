"""Rule-based GTO poker hand analyzer.

Produces the same JSON structure as the Claude-based endpoint so the
frontend requires no changes.
"""
from __future__ import annotations

from app.poker_engine.cards import Card, parse_hand, hand_category, board_texture
from app.poker_engine.ranges import hand_in_range, pos_range_pct
from app.poker_engine.pot_tracker import PotTracker

_BETTING_ACTIONS = frozenset({'CALL', 'BET', 'RAISE', 'ALL_IN'})


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def analyze(hand) -> dict:
    """Analyze a Hand ORM object and return analysis dict (same shape as Claude)."""
    hero = next((p for p in hand.players if p.is_hero), None)
    hero_name: str = hero.name if hero else ""
    hero_cards: list[Card] | None = parse_hand(hand.hero_cards)

    sorted_actions = sorted(hand.actions, key=lambda a: a.sequence)

    def by_street(street: str) -> list:
        return [a for a in sorted_actions if a.street == street]

    pot = PotTracker(initial_pot=1.5)
    result_straten: dict = {}
    fouten: list[dict] = []
    score_delta = 0

    # ---- PREFLOP ----
    pf_acts = by_street('PREFLOP')
    if hand.is_fast_fold:
        result_straten['PREFLOP'] = {
            'beoordeling': 'goed',
            'uitleg': (
                f"Hero maakt correct gebruik van fast-fold vanuit "
                f"{hand.hero_position or 'onbekende positie'} met "
                f"{hand.hero_cards or '?'}. Geen verdere actie nodig."
            ),
        }
    else:
        pf = _analyze_preflop(hand, hero_name, hero_cards, pf_acts)
        result_straten['PREFLOP'] = {
            'beoordeling': pf['beoordeling'],
            'uitleg': pf['uitleg'],
        }
        fouten.extend(pf['fouten'])
        score_delta += pf['score_delta']
    for a in pf_acts:
        pot.process_action(a)

    # ---- FLOP ----
    fl_acts = by_street('FLOP')
    if fl_acts or hand.flop_cards:
        board = hand.flop_cards.split() if hand.flop_cards else []
        fl = _analyze_postflop_street(
            'FLOP', fl_acts, hero_name, pot,
            board_texture(board), is_river=False,
        )
        if fl:
            result_straten['FLOP'] = {'beoordeling': fl['beoordeling'], 'uitleg': fl['uitleg']}
            fouten.extend(fl['fouten'])
            score_delta += fl['score_delta']
        for a in fl_acts:
            pot.process_action(a)

    # ---- TURN ----
    tn_acts = by_street('TURN')
    if tn_acts or hand.turn_card:
        board = (hand.flop_cards.split() if hand.flop_cards else []) + (
            [hand.turn_card] if hand.turn_card else []
        )
        tn = _analyze_postflop_street(
            'TURN', tn_acts, hero_name, pot,
            board_texture(board), is_river=False,
        )
        if tn:
            result_straten['TURN'] = {'beoordeling': tn['beoordeling'], 'uitleg': tn['uitleg']}
            fouten.extend(tn['fouten'])
            score_delta += tn['score_delta']
        for a in tn_acts:
            pot.process_action(a)

    # ---- RIVER ----
    rv_acts = by_street('RIVER')
    if rv_acts or hand.river_card:
        board = (
            (hand.flop_cards.split() if hand.flop_cards else [])
            + ([hand.turn_card] if hand.turn_card else [])
            + ([hand.river_card] if hand.river_card else [])
        )
        rv = _analyze_postflop_street(
            'RIVER', rv_acts, hero_name, pot,
            board_texture(board), is_river=True,
        )
        if rv:
            result_straten['RIVER'] = {'beoordeling': rv['beoordeling'], 'uitleg': rv['uitleg']}
            fouten.extend(rv['fouten'])
            score_delta += rv['score_delta']

    score = max(1, min(10, 8 + score_delta))

    return {
        'samenvatting': _build_samenvatting(hand, hero_cards),
        'straten': result_straten,
        'fouten': fouten,
        'score': score,
        'conclusie': _build_conclusie(fouten, score),
    }


# ---------------------------------------------------------------------------
# Preflop analysis
# ---------------------------------------------------------------------------

def _analyze_preflop(
    hand, hero_name: str, hero_cards: list[Card] | None, actions: list,
) -> dict:
    fouten: list[dict] = []
    score_delta = 0
    beoordeling = 'goed'
    uitleg_parts: list[str] = []

    pos = hand.hero_position or 'onbekend'
    cards_str = hand.hero_cards or '?'

    if not hero_cards:
        return {
            'beoordeling': 'goed',
            'uitleg': f"Preflop gespeeld vanuit {pos}.",
            'fouten': [],
            'score_delta': 0,
        }

    cat = hand_category(*hero_cards)
    in_range = hand_in_range(hero_cards[0], hero_cards[1], pos)

    hero_acts = [a for a in actions if a.player_name == hero_name]
    hero_raised = any(a.action_type in ('RAISE', 'BET') for a in hero_acts)
    hero_folded = any(a.action_type in ('FOLD', 'FAST_FOLD') for a in hero_acts)

    # 1. Opening with hand outside range
    if not in_range and hero_raised and cat == 'weak':
        fouten.append({
            'straat': 'PREFLOP',
            'moment': f"Hero opent {cards_str} vanuit {pos}",
            'probleem': (
                f"{cards_str} valt buiten de standaard opening range voor "
                f"{pos} (~{pos_range_pct(pos)}%). Je speelt te loose."
            ),
            'beter': (
                f"Fold {cards_str} vanuit {pos} en wacht op een hand "
                f"die in de standaard range past."
            ),
        })
        beoordeling = 'fout'
        score_delta -= 2
    elif not in_range and hero_raised:
        # Marginal — outside range but not terrible
        uitleg_parts.append(
            f"{cards_str} ligt net buiten de ideale {pos} opening range, "
            f"maar is speelbaar in bepaalde omstandigheden."
        )
        beoordeling = 'acceptabel'
        score_delta -= 1
    elif in_range and hero_raised:
        uitleg_parts.append(f"Correcte opening met {cards_str} vanuit {pos}.")

    # 2. Premium/strong hand not raised (missed value)
    if (
        cat in ('premium', 'strong')
        and not hero_raised
        and not hero_folded
        and pos in ('BTN', 'CO', 'HJ', 'SB')
    ):
        fouten.append({
            'straat': 'PREFLOP',
            'moment': f"Hero limpt/callt met {cards_str} vanuit {pos}",
            'probleem': (
                f"{cards_str} is een sterke hand. Limpen of callen laat "
                f"tegenstanders goedkope odds om equity te realiseren."
            ),
            'beter': (
                f"Open-raise met {cards_str} vanuit {pos} "
                f"(standaard 2.5–3BB) om de pot op te bouwen."
            ),
        })
        if beoordeling == 'goed':
            beoordeling = 'acceptabel'
        score_delta -= 1

    # 3. Sizing checks
    hero_raise_acts = [
        a for a in hero_acts
        if a.action_type in ('RAISE', 'BET') and a.amount_bb
    ]
    for raise_act in hero_raise_acts:
        amt = raise_act.amount_bb
        prev_raises = [
            a for a in actions
            if a.sequence < raise_act.sequence
            and a.action_type in ('RAISE', 'BET')
            and a.amount_bb
        ]

        if not prev_raises:
            # Open raise: 2–4BB is standard
            if amt < 1.5:
                fouten.append({
                    'straat': 'PREFLOP',
                    'moment': f"Hero opent voor {amt:.1f}BB",
                    'probleem': (
                        f"Open van {amt:.1f}BB is te klein. "
                        f"Tegenstanders kunnen winstgevend callen met brede range."
                    ),
                    'beter': "Gebruik een open van 2–3BB (standaard 6-max sizing).",
                })
                beoordeling = 'fout' if amt < 1.0 else 'acceptabel'
                score_delta -= 1
            elif amt > 5:
                fouten.append({
                    'straat': 'PREFLOP',
                    'moment': f"Hero opent voor {amt:.1f}BB",
                    'probleem': (
                        f"Open van {amt:.1f}BB is te groot. "
                        f"Je verliest actie van zwakkere handen."
                    ),
                    'beter': "Gebruik een open van 2–3BB voor optimale pot geometry.",
                })
                if beoordeling == 'goed':
                    beoordeling = 'acceptabel'
                score_delta -= 1
            elif not uitleg_parts:
                uitleg_parts.append(f"Solide open raise van {amt:.1f}BB vanuit {pos}.")
        else:
            # 3-bet: should be ~3× previous raise (min 10BB)
            prev_amt = prev_raises[-1].amount_bb
            expected = max(prev_amt * 3.0, 10.0)
            if amt < expected * 0.55:
                fouten.append({
                    'straat': 'PREFLOP',
                    'moment': f"Hero 3-bet naar {amt:.1f}BB over open van {prev_amt:.1f}BB",
                    'probleem': (
                        f"3-bet sizing van {amt:.1f}BB is te klein "
                        f"(ideaal ~{expected:.0f}BB). "
                        f"Tegenstanders callen te goedkoop en realiseren equity."
                    ),
                    'beter': f"3-bet naar minimaal {expected:.0f}BB voor correcte pot geometry.",
                })
                beoordeling = 'fout'
                score_delta -= 2

    # Default uitleg if nothing added yet
    if not uitleg_parts:
        if hero_folded:
            if in_range:
                uitleg_parts.append(
                    f"Hero foldt {cards_str} vanuit {pos}. "
                    f"Deze hand ligt in de standaard range — raise was ook een optie."
                )
            else:
                uitleg_parts.append(
                    f"Correcte fold van {cards_str} vanuit {pos} — hand buiten range."
                )
        else:
            uitleg_parts.append(f"Preflop gespeeld vanuit {pos} met {cards_str}.")

    return {
        'beoordeling': beoordeling,
        'uitleg': ' '.join(uitleg_parts),
        'fouten': fouten,
        'score_delta': score_delta,
    }


# ---------------------------------------------------------------------------
# Postflop analysis (FLOP / TURN / RIVER)
# ---------------------------------------------------------------------------

def _analyze_postflop_street(
    street: str,
    actions: list,
    hero_name: str,
    pot: PotTracker,
    texture: dict,
    is_river: bool,
) -> dict | None:
    hero_acts = [a for a in actions if a.player_name == hero_name]
    if not hero_acts:
        return None

    fouten: list[dict] = []
    score_delta = 0
    uitleg_parts: list[str] = []
    wet = texture.get('wet', False)

    # Track pot within this street so we have pot BEFORE each hero action
    local_pot = pot.pot

    for action in sorted(actions, key=lambda a: a.sequence):
        is_hero_action = action.player_name == hero_name
        if is_hero_action:
            pot_before = local_pot

            if action.action_type in ('BET', 'RAISE') and action.amount_bb:
                amt = action.amount_bb
                pct = (amt / pot_before * 100) if pot_before > 0 else 100.0
                result = _check_bet_sizing(
                    street, amt, pct, pot_before, wet, is_river
                )
                if result['is_fout']:
                    fouten.append(result['fout'])
                    score_delta -= 2 if result['is_major'] else 1
                else:
                    uitleg_parts.append(result['uitleg'])

            elif action.action_type == 'CALL' and action.amount_bb:
                call_amt = action.amount_bb
                if pot_before > 0:
                    req_eq = (call_amt / (pot_before + call_amt)) * 100
                    bet_pct = (call_amt / pot_before) * 100
                    if is_river and bet_pct > 100:
                        fouten.append({
                            'straat': street,
                            'moment': (
                                f"Hero callt {call_amt:.1f}BB river overbet "
                                f"in pot van {pot_before:.1f}BB ({bet_pct:.0f}% pot)"
                            ),
                            'probleem': (
                                f"Call van overbet ({bet_pct:.0f}% pot) vereist "
                                f"~{req_eq:.0f}% equity. Een overbet range is sterk "
                                f"gepolariseerd — bijna altijd de nuts."
                            ),
                            'beter': (
                                "Fold tenzij hero een tophanden heeft. "
                                "Villain's overbet range verslaat een gemiddelde hand."
                            ),
                        })
                        score_delta -= 1
                    else:
                        uitleg_parts.append(
                            f"Call van {call_amt:.1f}BB "
                            f"({bet_pct:.0f}% pot — {req_eq:.0f}% equity vereist)."
                        )

            elif action.action_type == 'FOLD':
                last_bet = _last_bet_before(actions, action.sequence)
                if last_bet and pot_before > 0:
                    bet_pct = (last_bet / pot_before) * 100
                    req_eq = (last_bet / (pot_before + last_bet)) * 100
                    if bet_pct < 20 and is_river:
                        fouten.append({
                            'straat': street,
                            'moment': (
                                f"Hero foldt tegen {last_bet:.1f}BB bet "
                                f"in pot van {pot_before:.1f}BB ({bet_pct:.0f}% pot)"
                            ),
                            'probleem': (
                                f"Fold tegen slechts {bet_pct:.0f}% pot bet. "
                                f"Je had maar {req_eq:.0f}% equity nodig om winstgevend te callen."
                            ),
                            'beter': (
                                f"Bij een bet van <20% pot is callen bijna altijd correct "
                                f"({req_eq:.0f}% equity vereist is zeer haalbaar)."
                            ),
                        })
                        score_delta -= 2

        # Update local pot after any player's action
        if action.amount_bb and action.action_type in _BETTING_ACTIONS:
            local_pot += action.amount_bb

    # Determine beoordeling from fouten severity
    if not fouten:
        beoordeling = 'goed'
    elif score_delta <= -2:
        beoordeling = 'fout'
    else:
        beoordeling = 'acceptabel'

    if not uitleg_parts and not fouten:
        uitleg_parts.append(f"Hero speelde de {street.lower()} correct.")
    elif not uitleg_parts:
        uitleg_parts.append(f"Verbeterpunt gevonden in de {street.lower()}.")

    return {
        'beoordeling': beoordeling,
        'uitleg': ' '.join(uitleg_parts),
        'fouten': fouten,
        'score_delta': score_delta,
    }


def _check_bet_sizing(
    street: str, amt: float, pct: float, pot_before: float,
    wet: bool, is_river: bool,
) -> dict:
    """Return sizing assessment as a dict with is_fout, fout, is_major, uitleg."""
    board_desc = "nat" if wet else "droog"
    ideal = "60–100%" if is_river else ("50–75%" if wet else "33–50%")

    if is_river:
        if pct < 25:
            return {
                'is_fout': True, 'is_major': False,
                'fout': {
                    'straat': street,
                    'moment': f"Hero bet {amt:.1f}BB in pot van {pot_before:.1f}BB ({pct:.0f}% pot)",
                    'probleem': (
                        f"River bet van {pct:.0f}% pot is te klein. "
                        f"Je laat waarde liggen en geeft tegenstanders gunstige odds."
                    ),
                    'beter': "Gebruik een river bet van 60–100% pot voor maximale waarde.",
                },
                'uitleg': '',
            }
        if pct > 150:
            return {
                'is_fout': True, 'is_major': False,
                'fout': {
                    'straat': street,
                    'moment': f"Hero bet {amt:.1f}BB in pot van {pot_before:.1f}BB ({pct:.0f}% pot)",
                    'probleem': (
                        f"Overbet van {pct:.0f}% pot op de river. "
                        f"Dit werkt alleen met een gepolariseerde range (nuts of bluff)."
                    ),
                    'beter': (
                        "Gebruik 75–100% pot voor value bets. "
                        "Overbet alleen met nuts of als specifieke bluff."
                    ),
                },
                'uitleg': '',
            }
        return {
            'is_fout': False, 'is_major': False, 'fout': {},
            'uitleg': f"Solide river bet van {pct:.0f}% pot ({amt:.1f}BB).",
        }

    # Flop / Turn
    if pct < 20:
        return {
            'is_fout': True, 'is_major': True,
            'fout': {
                'straat': street,
                'moment': f"Hero bet {amt:.1f}BB in pot van {pot_before:.1f}BB ({pct:.0f}% pot)",
                'probleem': (
                    f"Bet van {pct:.0f}% pot is te klein — tegenstanders kunnen "
                    f"winstgevend callen met alle draws en zwakke handen."
                ),
                'beter': f"Gebruik {ideal} pot sizing op {board_desc} board voor correcte fold equity.",
            },
            'uitleg': '',
        }
    if pct > 120:
        return {
            'is_fout': True, 'is_major': False,
            'fout': {
                'straat': street,
                'moment': f"Hero bet {amt:.1f}BB in pot van {pot_before:.1f}BB ({pct:.0f}% pot)",
                'probleem': (
                    f"Overbet van {pct:.0f}% pot. "
                    f"Tegenstanders kunnen tight folden met zwakke handen "
                    f"en callen/raisen met nuts."
                ),
                'beter': f"Gebruik {ideal} pot sizing voor een brede waarde-range op {board_desc} board.",
            },
            'uitleg': '',
        }

    return {
        'is_fout': False, 'is_major': False, 'fout': {},
        'uitleg': f"Correcte bet van {pct:.0f}% pot ({amt:.1f}BB) op {board_desc} board.",
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _last_bet_before(actions: list, sequence: int) -> float | None:
    bets = [
        a.amount_bb for a in actions
        if a.sequence < sequence
        and a.action_type in ('BET', 'RAISE')
        and a.amount_bb
    ]
    return bets[-1] if bets else None


def _build_samenvatting(hand, hero_cards: list[Card] | None) -> str:
    pos = hand.hero_position or 'onbekende positie'
    cards_str = hand.hero_cards or '?'
    profit_str = f"{hand.hero_profit_bb:+.1f}BB"

    if hand.is_fast_fold:
        return (
            f"Hero fast-folde vanuit {pos} met {cards_str}. "
            f"Snelle exit zonder verdere actie."
        )

    cat_nl = 'hand'
    if hero_cards:
        cat = hand_category(*hero_cards)
        cat_nl = {
            'premium': 'premium hand', 'strong': 'sterke hand',
            'speculative': 'speculatieve hand', 'weak': 'zwakke hand',
        }.get(cat, 'hand')

    if hand.hero_went_to_showdown:
        outcome = 'showdown gewonnen' if hand.hero_won_at_showdown else 'showdown verloren'
    elif hand.hero_profit_bb > 0:
        outcome = 'gewonnen'
    elif hand.hero_profit_bb < 0:
        outcome = 'verloren'
    else:
        outcome = 'break-even'

    return (
        f"Hero speelt een {cat_nl} ({cards_str}) vanuit {pos} en eindigt "
        f"{outcome} ({profit_str})."
    )


def _build_conclusie(fouten: list, score: int) -> str:
    n = len(fouten)
    if n == 0:
        if score >= 9:
            return (
                "Uitstekend gespeeld. Hero maakte solide beslissingen in lijn "
                "met GTO-principes en maximaliseerde de verwachte waarde."
            )
        return (
            "Redelijke hand zonder grote fouten. "
            "Blijf werken aan bet-sizing consistentie voor verdere verbetering."
        )
    streets = list(dict.fromkeys(f['straat'] for f in fouten))
    streets_str = ', '.join(s.lower() for s in streets)
    if n == 1:
        return (
            f"Eén verbeterpunt op de {streets_str}. "
            f"Focus op de bet-sizing en positional awareness om de EV te verbeteren."
        )
    return (
        f"{n} verbeterpunten gevonden (op {streets_str}). "
        f"Besteed bijzondere aandacht aan bet-sizing keuzes en pot odds berekeningen."
    )
