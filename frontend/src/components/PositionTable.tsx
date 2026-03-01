import { usePositionStats } from '../hooks/useStats'
import { Card } from './ui/Card'
import { Spinner } from './ui/Spinner'
import { formatPct, profitColor } from '../lib/utils'

export function PositionTable() {
  const { data: stats, isLoading } = usePositionStats()

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold text-zinc-100 mb-5">Positie Analyse</h1>

      <Card className="p-0 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-32"><Spinner /></div>
        ) : !stats?.length ? (
          <div className="p-8 text-center text-zinc-600 text-sm">Geen data beschikbaar</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800 text-zinc-500 text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3">Positie</th>
                <th className="text-right px-4 py-3">Handen</th>
                <th className="text-right px-4 py-3">VPIP</th>
                <th className="text-right px-4 py-3">PFR</th>
                <th className="text-right px-4 py-3">3-Bet</th>
                <th className="text-right px-4 py-3">BB/100</th>
                <th className="text-right px-4 py-3">Totaal</th>
              </tr>
            </thead>
            <tbody>
              {stats.map((row) => (
                <tr key={row.position} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                  <td className="px-4 py-3 font-mono font-bold text-zinc-200">{row.position}</td>
                  <td className="px-4 py-3 text-right text-zinc-400">{row.hands}</td>
                  <td className="px-4 py-3 text-right text-zinc-300">{formatPct(row.vpip)}</td>
                  <td className="px-4 py-3 text-right text-zinc-300">{formatPct(row.pfr)}</td>
                  <td className="px-4 py-3 text-right text-zinc-300">{formatPct(row.three_bet_pct)}</td>
                  <td className={`px-4 py-3 text-right font-medium ${profitColor(row.bb_per_100)}`}>
                    {row.bb_per_100 >= 0 ? '+' : ''}{row.bb_per_100.toFixed(2)}
                  </td>
                  <td className={`px-4 py-3 text-right font-mono ${profitColor(row.total_profit_bb)}`}>
                    {row.total_profit_bb >= 0 ? '+' : ''}{row.total_profit_bb.toFixed(1)} BB
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      {/* Rush & Cash uitleg */}
      <div className="mt-4 bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-500">
        <p>
          <span className="text-zinc-400 font-medium">Rush & Cash tip:</span>{' '}
          Positie roteert bij elke hand, dus grote samples per positie zijn nodig voor betrouwbare stats.
          Bij minder dan 200 handen per positie moet je de cijfers met voorzichtigheid interpreteren.
        </p>
      </div>
    </div>
  )
}
