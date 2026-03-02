import { useOverviewStats, useTimeline } from '../hooks/useStats'
import { StatsGrid } from './StatsGrid'
import { WinrateChart } from './WinrateChart'
import { BulkAnalysisPanel } from './BulkAnalysisPanel'

export function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useOverviewStats()
  const { data: timeline, isLoading: timelineLoading } = useTimeline()

  const noData = !statsLoading && stats?.total_hands === 0

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-zinc-100">Dashboard</h1>
        {stats?.total_hands ? (
          <p className="text-sm text-zinc-500 mt-0.5">
            {stats.total_hands.toLocaleString()} handen geanalyseerd
          </p>
        ) : null}
      </div>

      {noData ? (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-10 text-center">
          <p className="text-zinc-400 text-lg mb-2">Nog geen handen geïmporteerd</p>
          <p className="text-zinc-600 text-sm">
            Ga naar <span className="text-green-400">Import</span> om een GGPoker hand history .txt te uploaden
          </p>
        </div>
      ) : (
        <>
          <StatsGrid stats={stats} isLoading={statsLoading} />
          <WinrateChart data={timeline} isLoading={timelineLoading} />
          <BulkAnalysisPanel />
        </>
      )}
    </div>
  )
}
