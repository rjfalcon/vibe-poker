export function HelpPage() {
  return (
    <div className="p-6 max-w-3xl">
      <h1 className="text-xl font-bold text-zinc-100 mb-8">Uitleg & Afkortingen</h1>

      {/* How it works */}
      <section className="mb-10">
        <h2 className="text-base font-semibold text-zinc-200 mb-4 pb-2 border-b border-zinc-800">
          Hoe werkt de app?
        </h2>
        <ol className="space-y-3 text-sm text-zinc-400">
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-900/50 text-green-400 text-xs flex items-center justify-center font-bold">1</span>
            <span>
              <span className="text-zinc-200 font-medium">Exporteer je hand history</span> vanuit de GGPoker client via{' '}
              <span className="text-zinc-300">Menu → Hand History</span>. Selecteer het type{' '}
              <span className="text-zinc-300">Rush & Cash</span> en exporteer als <code className="text-green-400">.txt</code>.
            </span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-900/50 text-green-400 text-xs flex items-center justify-center font-bold">2</span>
            <span>
              <span className="text-zinc-200 font-medium">Importeer via de Import-pagina.</span>{' '}
              Je kunt meerdere bestanden tegelijk slepen. Duplicaten worden automatisch overgeslagen.
            </span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-900/50 text-green-400 text-xs flex items-center justify-center font-bold">3</span>
            <span>
              <span className="text-zinc-200 font-medium">Analyseer op het Dashboard.</span>{' '}
              Statistieken worden direct berekend over alle geïmporteerde handen.
            </span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-900/50 text-green-400 text-xs flex items-center justify-center font-bold">4</span>
            <span>
              <span className="text-zinc-200 font-medium">Bekijk individuele handen</span> via de Handen-pagina.
              Filter op positie, fast fold, street bereikt of winst/verlies. Klik op een hand voor het volledige replay-overzicht.
            </span>
          </li>
        </ol>
      </section>

      {/* Preflop stats */}
      <section className="mb-10">
        <h2 className="text-base font-semibold text-zinc-200 mb-4 pb-2 border-b border-zinc-800">
          Preflop statistieken
        </h2>
        <div className="space-y-4">
          <StatRow abbr="VPIP" full="Voluntarily Put money In Pot">
            Percentage handen waarin je vrijwillig preflop geld in de pot hebt gestopt (callen of raisen).
            Blinds posten telt <em>niet</em> mee. Een typische waarde voor 6-max is 22–30%.
            Hoger = looser, lager = tighter.
          </StatRow>
          <StatRow abbr="PFR" full="Pre-Flop Raise">
            Percentage handen waarin je preflop hebt geraisd. Altijd ≤ VPIP.
            Een gezonde PFR ligt dicht bij VPIP (b.v. VPIP 25 / PFR 20).
            Een groot verschil wijst op veel passief callen.
          </StatRow>
          <StatRow abbr="3-bet%" full="Three-Bet Percentage">
            Hoe vaak je re-raiset wanneer er al een open-raise voor je is.
            Gemeten als percentage van de momenten dat je een 3-bet <em>kán</em> maken.
            Typisch 6–10% in 6-max cash games.
          </StatRow>
          <StatRow abbr="FF%" full="Fast Fold Percentage">
            Percentage handen dat je direct gefolded hebt via de Fast Fold knop, vóór de actie aan jou was.
            Rush &amp; Cash-specifiek. Hoge FF% betekent dat je selectief speelt met je starthandenrange.
          </StatRow>
        </div>
      </section>

      {/* Postflop stats */}
      <section className="mb-10">
        <h2 className="text-base font-semibold text-zinc-200 mb-4 pb-2 border-b border-zinc-800">
          Postflop statistieken
        </h2>
        <div className="space-y-4">
          <StatRow abbr="AF" full="Aggression Factor">
            Verhouding tussen agressieve acties (bet + raise) en passieve acties (call).
            Formule: <code className="text-zinc-300">(bet + raise) / call</code>.
            Waarde boven 2 = agressief, onder 1 = passief/sticky. Typisch 2–4 voor goede spelers.
          </StatRow>
          <StatRow abbr="WTSD" full="Went To ShowDown">
            Percentage handen dat je de showdown bereikt hebt, gegeven dat je de flop hebt gezien.
            Hoge WTSD (boven 30%) kan wijzen op te veel showdowns met zwakke handen.
            Typisch 25–30%.
          </StatRow>
          <StatRow abbr="W$SD" full="Won money at ShowDown">
            Percentage showdowns dat je gewonnen hebt. Onder 50% is verliesgevend op showdowns.
            Typisch 50–55% voor een winnende speler.
          </StatRow>
        </div>
      </section>

      {/* Winrate */}
      <section className="mb-10">
        <h2 className="text-base font-semibold text-zinc-200 mb-4 pb-2 border-b border-zinc-800">
          Winrate & resultaat
        </h2>
        <div className="space-y-4">
          <StatRow abbr="BB/100" full="Big Blinds per 100 handen">
            De standaardmaat voor winrate in cash games. Hoeveel grote blinds je gemiddeld wint of
            verliest per 100 gespeelde handen. Een break-even speler zit op 0. Rake eten mee.
            Een goede winrate in microstakes is +5 tot +15 BB/100.
          </StatRow>
          <StatRow abbr="BB" full="Big Blind">
            De grote blind — de basiseenheid voor bedragen in deze app.
            Bij $0.02/$0.05 is 1 BB = $0.05. Winst en verlies worden altijd in BB uitgedrukt
            zodat je resultaten over verschillende stakes kunt vergelijken.
          </StatRow>
          <StatRow abbr="SB" full="Small Blind">
            De kleine blind, de helft van de big blind. Bij $0.02/$0.05 is 1 SB = $0.02.
          </StatRow>
        </div>
      </section>

      {/* Positions */}
      <section className="mb-10">
        <h2 className="text-base font-semibold text-zinc-200 mb-4 pb-2 border-b border-zinc-800">
          Posities (6-max)
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
          {[
            { abbr: 'BTN', full: 'Button', desc: 'Laatste om te acteren postflop. Sterkste positie.' },
            { abbr: 'CO', full: 'Cutoff', desc: 'Één voor de button. Tweede sterkste positie.' },
            { abbr: 'HJ', full: 'Hijack', desc: 'Twee voor de button.' },
            { abbr: 'MP', full: 'Middle Position', desc: 'Middelste positie in 6-max.' },
            { abbr: 'UTG', full: 'Under The Gun', desc: 'Eerste om preflop te acteren. Zwakste positie.' },
            { abbr: 'SB', full: 'Small Blind', desc: 'Eerste om postflop te acteren. Op één na zwakste.' },
            { abbr: 'BB', full: 'Big Blind', desc: 'Laatste om preflop te acteren (na de deal).' },
          ].map(({ abbr, full, desc }) => (
            <div key={abbr} className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3">
              <div className="flex items-baseline gap-2 mb-1">
                <span className="font-mono font-bold text-green-400">{abbr}</span>
                <span className="text-zinc-500 text-xs">{full}</span>
              </div>
              <p className="text-zinc-400 text-xs">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Hand tags */}
      <section>
        <h2 className="text-base font-semibold text-zinc-200 mb-4 pb-2 border-b border-zinc-800">
          Labels in de handentabel
        </h2>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-3">
            <span className="px-2 py-0.5 rounded text-xs font-medium bg-zinc-700 text-zinc-300">FF</span>
            <span className="text-zinc-400">Fast Fold — je hebt de hand direct gefolded vóór de actie aan jou was.</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-900/60 text-blue-300">RIT</span>
            <span className="text-zinc-400">Run It Twice — de board is twee keer uitgedeeld (bij all-in).</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-2 py-0.5 rounded text-xs font-medium bg-amber-900/60 text-amber-300">PFR</span>
            <span className="text-zinc-400">Pre-Flop Raise — je hebt preflop geraisd in deze hand.</span>
          </div>
        </div>
      </section>
    </div>
  )
}

function StatRow({
  abbr,
  full,
  children,
}: {
  abbr: string
  full: string
  children: React.ReactNode
}) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3">
      <div className="flex items-baseline gap-2 mb-1.5">
        <span className="font-mono font-bold text-green-400">{abbr}</span>
        <span className="text-zinc-500 text-xs">{full}</span>
      </div>
      <p className="text-zinc-400 text-sm leading-relaxed">{children}</p>
    </div>
  )
}
