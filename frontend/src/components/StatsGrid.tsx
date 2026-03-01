import { Card, CardTitle } from './ui/Card'
import { Spinner } from './ui/Spinner'
import type { OverviewStats } from '../types'
import { formatBB, formatPct, profitColor } from '../lib/utils'

interface StatCardProps {
  label: string
  value: string
  sub?: string
  valueClass?: string
}

function StatCard({ label, value, sub, valueClass = 'text-zinc-100' }: StatCardProps) {
  return (
    <Card className="flex flex-col gap-1">
      <CardTitle>{label}</CardTitle>
      <p className={`text-2xl font-bold ${valueClass}`}>{value}</p>
      {sub && <p className="text-xs text-zinc-500">{sub}</p>}
    </Card>
  )
}

interface Props {
  stats: OverviewStats | undefined
  isLoading: boolean
}

export function StatsGrid({ stats, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <Spinner />
      </div>
    )
  }
  if (!stats) return null

  const winrateClass = profitColor(stats.bb_per_100)

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
      <StatCard
        label="BB/100"
        value={`${stats.bb_per_100 >= 0 ? '+' : ''}${stats.bb_per_100.toFixed(2)}`}
        sub={`${formatBB(stats.total_profit_bb)} totaal`}
        valueClass={winrateClass}
      />
      <StatCard label="Handen" value={stats.total_hands.toLocaleString()} />
      <StatCard
        label="VPIP"
        value={formatPct(stats.vpip)}
        sub={`PFR ${formatPct(stats.pfr)}`}
      />
      <StatCard
        label="3-Bet %"
        value={formatPct(stats.three_bet_pct)}
      />
      <StatCard
        label="AF"
        value={stats.af.toFixed(2)}
        sub="Agressie Factor"
      />
      <StatCard
        label="WTSD"
        value={formatPct(stats.wtsd)}
        sub={`W$SD ${formatPct(stats.wsd)}`}
      />
      <StatCard
        label="Fast-Fold %"
        value={formatPct(stats.fast_fold_pct)}
        sub={`${stats.hands_fast_folded.toLocaleString()} handen`}
        valueClass="text-zinc-400"
      />
      <StatCard
        label="Rake"
        value={`${stats.rake_bb.toFixed(1)} BB`}
        sub="totaal betaald"
        valueClass="text-red-400"
      />
    </div>
  )
}
