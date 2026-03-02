"""Bulk analysis: detect leaks and strengths across the full hand history."""
from __future__ import annotations

from app.stats.engine import OverviewStats, PositionStats

# ---------------------------------------------------------------------------
# GTO benchmarks for 6-max Rush & Cash
# Ranges apply to stats computed on NON-fast-fold hands (played-out hands).
# ---------------------------------------------------------------------------

# Effective VPIP/PFR benchmarks (among played-out hands)
_VPIP_LOW  = 15.0
_VPIP_HIGH = 32.0
_PFR_LOW   = 12.0
_PFR_HIGH  = 24.0
_RATIO_LOW = 0.60  # PFR/VPIP

# Preflop aggression
_THREE_BET_LOW  = 5.0
_THREE_BET_HIGH = 15.0

# Postflop aggression
_AF_LOW  = 1.5
_AF_HIGH = 5.5

# Showdown discipline
_WTSD_LOW  = 18.0
_WTSD_HIGH = 30.0
_WSD_LOW   = 44.0

# Position: losing more than -5 BB/100 from a position is a leak
_POSITION_LOSS_THRESHOLD = -5.0


def bulk_analyze(
    overview: OverviewStats,
    positions: list[PositionStats],
) -> dict:
    """Return aggregate analysis using GTO benchmarks."""

    leaks: list[dict] = []
    sterke_punten: list[dict] = []

    min_hands = 50
    if overview.total_hands < min_hands:
        return {
            "total_hands": overview.total_hands,
            "hands_analyzed": overview.hands_played_out,
            "overall_score": None,
            "winrate_bb100": overview.bb_per_100,
            "leaks": [],
            "sterke_punten": [],
            "samenvatting": (
                f"Nog te weinig handen ({overview.total_hands}) voor betrouwbare analyse. "
                f"Importeer minimaal {min_hands} handen voor zinvolle patronen."
            ),
            "conclusie": f"Minimaal {min_hands} handen vereist.",
        }

    played = overview.hands_played_out or 1

    # Effective VPIP/PFR on played-out hands (excludes fast-folds)
    vpip_count = overview.vpip * overview.total_hands / 100
    pfr_count  = overview.pfr  * overview.total_hands / 100
    eff_vpip = round(vpip_count / played * 100, 1)
    eff_pfr  = round(pfr_count  / played * 100, 1)

    # ---- VPIP ----
    if eff_vpip > _VPIP_HIGH:
        leaks.append({
            "categorie": "Preflop range",
            "ernst": "major" if eff_vpip > 38 else "minor",
            "stat": f"VPIP {eff_vpip:.0f}%",
            "beschrijving": (
                f"Je speelt {eff_vpip:.0f}% van je handen mee — te ruim voor 6-max "
                f"(ideaal: {_VPIP_LOW:.0f}–{_VPIP_HIGH:.0f}%). "
                f"Dit duidt op te losse preflop range: je betaalt te veel om in potten te komen "
                f"met handen die negatieve verwachte waarde hebben."
            ),
            "advies": (
                "Fold meer handen preflop, vooral vanuit UTG/HJ. "
                "Focus op handen in je standaard positierange en laat marginal speculative hands gaan."
            ),
        })
    elif eff_vpip < _VPIP_LOW:
        leaks.append({
            "categorie": "Preflop range",
            "ernst": "minor",
            "stat": f"VPIP {eff_vpip:.0f}%",
            "beschrijving": (
                f"Je speelt slechts {eff_vpip:.0f}% van je handen mee — erg tight "
                f"(ideaal: {_VPIP_LOW:.0f}–{_VPIP_HIGH:.0f}%). "
                f"Je laat waarschijnlijk waarde liggen met speelbare handen, "
                f"en bent te voorspelbaar wanneer je wél meespeelt."
            ),
            "advies": (
                "Verbreed je range op de BTN en CO met suited connectors en broadway hands. "
                "Tegenstanders zullen je range met meer respekt behandelen."
            ),
        })
    else:
        sterke_punten.append({
            "categorie": "Preflop range",
            "beschrijving": (
                f"Solide VPIP van {eff_vpip:.0f}% — je selecteert handen goed "
                f"en speelt tight-aggressive preflop."
            ),
        })

    # ---- PFR / VPIP ratio ----
    if eff_vpip > 0:
        ratio = eff_pfr / eff_vpip
        if eff_pfr < _PFR_LOW:
            leaks.append({
                "categorie": "Preflop agressie",
                "ernst": "major",
                "stat": f"PFR {eff_pfr:.0f}%",
                "beschrijving": (
                    f"PFR van {eff_pfr:.0f}% is te laag (ideaal: {_PFR_LOW:.0f}–{_PFR_HIGH:.0f}%). "
                    f"Je limpt of callt te veel preflop in plaats van te raisen. "
                    f"Limpen verliest de initiative en geeft goedkope odds aan de blinds."
                ),
                "advies": (
                    "Raise open met alle handen waarmee je meedoet. "
                    "Verwijder limps volledig uit je game: raise of fold is de GTO-baseline."
                ),
            })
        elif ratio < _RATIO_LOW and eff_pfr >= _PFR_LOW:
            leaks.append({
                "categorie": "Preflop agressie",
                "ernst": "minor",
                "stat": f"PFR/VPIP {ratio:.2f}",
                "beschrijving": (
                    f"PFR/VPIP ratio van {ratio:.2f} is laag (ideaal: ≥0.65). "
                    f"Je speelt veel handen mee maar raiset minder dan je zou moeten — "
                    f"dit duidt op te veel calls en te weinig raises."
                ),
                "advies": (
                    "Vervang calls door raises of folds. "
                    "Elke hand die het waard is om mee te doen, is ook het waard om mee te raisen."
                ),
            })
        elif eff_pfr >= _PFR_LOW:
            sterke_punten.append({
                "categorie": "Preflop agressie",
                "beschrijving": (
                    f"Goede PFR van {eff_pfr:.0f}% met solide PFR/VPIP ratio ({ratio:.2f}) — "
                    f"je speelt tight-aggressive preflop."
                ),
            })

    # ---- 3-bet% ----
    if overview.three_bet_pct > 0 or overview.total_hands > 100:
        if overview.three_bet_pct < _THREE_BET_LOW:
            leaks.append({
                "categorie": "3-bet frequentie",
                "ernst": "minor",
                "stat": f"3-bet {overview.three_bet_pct:.1f}%",
                "beschrijving": (
                    f"3-bet percentage van {overview.three_bet_pct:.1f}% is laag "
                    f"(ideaal: {_THREE_BET_LOW:.0f}–{_THREE_BET_HIGH:.0f}%). "
                    f"Je geeft opens te makkelijk door en callt te vaak — dit is exploitabel."
                ),
                "advies": (
                    "3-bet meer vanuit de BTN en SB als defense, en voeg lichte 3-bet bluffs toe "
                    "met suited broadways (AJs, KQs) en suited connectors."
                ),
            })
        elif overview.three_bet_pct > _THREE_BET_HIGH:
            leaks.append({
                "categorie": "3-bet frequentie",
                "ernst": "minor",
                "stat": f"3-bet {overview.three_bet_pct:.1f}%",
                "beschrijving": (
                    f"3-bet percentage van {overview.three_bet_pct:.1f}% is hoog "
                    f"(ideaal: {_THREE_BET_LOW:.0f}–{_THREE_BET_HIGH:.0f}%). "
                    f"Je 3-bet te veel en wordt exploiteerbaar — goede regulars zullen 4-betten of callen met brede range."
                ),
                "advies": (
                    "Verklein je 3-bet range naar premium handen + specifieke bluffs. "
                    "Kies je bluffs zorgvuldig op blockers (Ax suited als bluff)."
                ),
            })
        else:
            sterke_punten.append({
                "categorie": "3-bet frequentie",
                "beschrijving": (
                    f"Gezonde 3-bet frequentie van {overview.three_bet_pct:.1f}% — "
                    f"je speelt agressief maar gecontroleerd preflop."
                ),
            })

    # ---- AF (Aggression Factor) ----
    if overview.af < _AF_LOW:
        leaks.append({
            "categorie": "Postflop agressie",
            "ernst": "major" if overview.af < 1.0 else "minor",
            "stat": f"AF {overview.af:.2f}",
            "beschrijving": (
                f"Aggression Factor van {overview.af:.2f} is laag (ideaal: {_AF_LOW:.1f}–{_AF_HIGH:.1f}). "
                f"Je speelt te passief postflop: te veel calls, te weinig bets en raises. "
                f"Passief spelen geeft tegenstanders gratis equity en mist waarde met sterke handen."
            ),
            "advies": (
                "Bet en raise vaker met je sterke handen en semi-bluffs. "
                "Check-call minder, check-raise meer op droge boards met tophanden. "
                "Doel: minimaal 2 bets/raises per call."
            ),
        })
    elif overview.af > _AF_HIGH:
        leaks.append({
            "categorie": "Postflop agressie",
            "ernst": "minor",
            "stat": f"AF {overview.af:.2f}",
            "beschrijving": (
                f"Aggression Factor van {overview.af:.2f} is hoog (ideaal: {_AF_LOW:.1f}–{_AF_HIGH:.1f}). "
                f"Je bent erg agressief postflop — tegenstanders zullen je vaker callen/raisen met draws."
            ),
            "advies": (
                "Balanceer je range beter: mix check-calls met je sterke handen "
                "om niet altijd polariseerd over te komen."
            ),
        })
    else:
        sterke_punten.append({
            "categorie": "Postflop agressie",
            "beschrijving": (
                f"Goede Aggression Factor van {overview.af:.2f} — "
                f"je speelt actief postflop zonder overagressief te zijn."
            ),
        })

    # ---- WTSD ----
    if overview.wtsd > _WTSD_HIGH:
        leaks.append({
            "categorie": "Showdown discipline",
            "ernst": "major" if overview.wtsd > 35 else "minor",
            "stat": f"WTSD {overview.wtsd:.1f}%",
            "beschrijving": (
                f"Je gaat {overview.wtsd:.1f}% van de flophanden naar showdown "
                f"(ideaal: {_WTSD_LOW:.0f}–{_WTSD_HIGH:.0f}%). "
                f"Dit is een klassiek 'calling station' patroon: je foldt te weinig op de turn en river."
            ),
            "advies": (
                "Fold meer op de turn en river tegen agressie als je geen sterke hand hebt. "
                "Als je WTSD hoog is maar W$SD ook hoog, dan selecteer je goed — maar let op bloated pots."
            ),
        })
    elif overview.wtsd < _WTSD_LOW:
        leaks.append({
            "categorie": "Showdown discipline",
            "ernst": "minor",
            "stat": f"WTSD {overview.wtsd:.1f}%",
            "beschrijving": (
                f"Je gaat slechts {overview.wtsd:.1f}% naar showdown "
                f"(ideaal: {_WTSD_LOW:.0f}–{_WTSD_HIGH:.0f}%). "
                f"Je foldt mogelijk te veel op latere streets en wordt geblufft."
            ),
            "advies": (
                "Call meer river bets met middelhoge handen die bluffs kloppen. "
                "Check de pot odds: een bet van 50% pot vereist slechts 33% equity."
            ),
        })
    else:
        sterke_punten.append({
            "categorie": "Showdown discipline",
            "beschrijving": (
                f"Goede WTSD van {overview.wtsd:.1f}% — "
                f"je selecteert goed wanneer je doorvecht en wanneer je foldt."
            ),
        })

    # ---- W$SD ----
    if overview.wtsd > 0 and overview.wsd < _WSD_LOW:
        leaks.append({
            "categorie": "Showdown kwaliteit",
            "ernst": "major",
            "stat": f"W$SD {overview.wsd:.1f}%",
            "beschrijving": (
                f"Je wint slechts {overview.wsd:.1f}% van je showdowns "
                f"(ideaal: >{_WSD_LOW:.0f}%). "
                f"Dit betekent dat je naar showdown gaat met te zwakke handen "
                f"of te vaak wordt opgeblufft."
            ),
            "advies": (
                "Fold meer op de river tegen sterke bets als je geen goede blockers hebt. "
                "Ga alleen naar showdown met handen die de villain's range verslaan."
            ),
        })
    elif overview.wsd >= 50:
        sterke_punten.append({
            "categorie": "Showdown kwaliteit",
            "beschrijving": (
                f"Goede W$SD van {overview.wsd:.1f}% — "
                f"je selecteert goed welke handen de showdown waard zijn."
            ),
        })

    # ---- Positie-analyse ----
    position_leaks: list[str] = []
    for p in positions:
        if p.hands >= 30 and p.bb_per_100 < _POSITION_LOSS_THRESHOLD:
            position_leaks.append(
                f"{p.position} ({p.hands} handen, {p.bb_per_100:+.1f} BB/100)"
            )
    if position_leaks:
        leaks.append({
            "categorie": "Positie-leaks",
            "ernst": "major" if len(position_leaks) >= 2 else "minor",
            "stat": f"{len(position_leaks)} positie(s) verliesgevend",
            "beschrijving": (
                f"Verliesgevende posities (< {_POSITION_LOSS_THRESHOLD:.0f} BB/100): "
                + ", ".join(position_leaks)
                + ". Dit wijst op onjuiste range selectie of postflop fouten vanuit die posities."
            ),
            "advies": (
                "Analyseer individuele handen vanuit verliesgevende posities. "
                "Verklein je range preflop in die posities en speel strakker postflop."
            ),
        })
    elif any(p.bb_per_100 >= 5 for p in positions if p.hands >= 30):
        best = max((p for p in positions if p.hands >= 30), key=lambda p: p.bb_per_100)
        sterke_punten.append({
            "categorie": "Positie-spel",
            "beschrijving": (
                f"Sterke winrate vanuit {best.position} ({best.bb_per_100:+.1f} BB/100 over {best.hands} handen). "
                f"Goede positional awareness."
            ),
        })

    # ---- Win rate ----
    if overview.bb_per_100 > 5:
        sterke_punten.append({
            "categorie": "Winrate",
            "beschrijving": (
                f"Winstgevend met {overview.bb_per_100:+.2f} BB/100 — "
                f"solide winrate boven het gemiddelde voor 6-max Rush & Cash."
            ),
        })
    elif overview.bb_per_100 < -3:
        leaks.append({
            "categorie": "Winrate",
            "ernst": "major",
            "stat": f"{overview.bb_per_100:+.2f} BB/100",
            "beschrijving": (
                f"Verliesgevend met {overview.bb_per_100:+.2f} BB/100. "
                f"De bovenstaande leaks dragen bij aan dit resultaat."
            ),
            "advies": "Los de geïdentificeerde leaks op in prioriteitsvolgorde (major eerst).",
        })

    # ---- Score ----
    major_count = sum(1 for l in leaks if l.get("ernst") == "major")
    minor_count = sum(1 for l in leaks if l.get("ernst") == "minor")
    score = max(1, min(10, 8 - major_count * 2 - minor_count))

    # ---- Samenvatting ----
    samenvatting = _build_samenvatting(overview, eff_vpip, eff_pfr, len(leaks))
    conclusie = _build_conclusie(leaks, sterke_punten, score, overview.bb_per_100)

    return {
        "total_hands": overview.total_hands,
        "hands_analyzed": overview.hands_played_out,
        "overall_score": score,
        "winrate_bb100": overview.bb_per_100,
        "leaks": leaks,
        "sterke_punten": sterke_punten,
        "samenvatting": samenvatting,
        "conclusie": conclusie,
    }


def _build_samenvatting(
    s: OverviewStats, eff_vpip: float, eff_pfr: float, n_leaks: int
) -> str:
    profiel = _player_profile(eff_vpip, eff_pfr, s.af)
    winrate_txt = (
        f"winstgevend ({s.bb_per_100:+.1f} BB/100)"
        if s.bb_per_100 > 0
        else f"verliesgevend ({s.bb_per_100:+.1f} BB/100)"
    )
    return (
        f"Analyse van {s.total_hands} handen ({s.hands_played_out} uitgespeeld, "
        f"{s.hands_fast_folded} fast-fold). "
        f"Speel­profiel: {profiel}. "
        f"Je bent momenteel {winrate_txt}. "
        f"{n_leaks} verbeterpunt{'en' if n_leaks != 1 else ''} geïdentificeerd."
    )


def _player_profile(vpip: float, pfr: float, af: float) -> str:
    tight = vpip < 20
    aggressive = pfr / vpip > 0.7 if vpip > 0 else False
    if tight and aggressive:
        return "Tight-Aggressive (TAG) — ideaal profiel voor 6-max"
    if tight and not aggressive:
        return "Tight-Passive (nit) — te weinig agressie"
    if not tight and aggressive:
        return "Loose-Aggressive (LAG) — speelbaar maar riskant"
    return "Loose-Passive (calling station) — verliesgevend profiel"


def _build_conclusie(leaks: list, sterke_punten: list, score: int, bb100: float) -> str:
    major = [l for l in leaks if l.get("ernst") == "major"]
    if not leaks:
        return (
            "Geen significante leaks gevonden. Blijf werken aan game-selectie "
            "en bet-sizing optimalisatie voor extra winrate."
        )
    if major:
        top = major[0]["categorie"].lower()
        return (
            f"Prioriteit: los de {top}-leak als eerste op — dit heeft de grootste impact op je winrate. "
            f"Met {score}/10 is er duidelijke ruimte voor verbetering. "
            f"{'Ondanks de leaks ben je winstgevend — goed teken.' if bb100 > 0 else 'De leaks verklaren de negatieve winrate.'}"
        )
    return (
        f"Kleine verbeterpunten gevonden (score: {score}/10). "
        f"Focus op de beschreven aanpassingen om van {bb100:+.1f} BB/100 naar hogere winrate te gaan."
    )
