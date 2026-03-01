import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, SlidersHorizontal } from 'lucide-react'
import { useHands } from '../hooks/useHands'
import { HoleCards } from './ui/PlayingCard'
import { Badge } from './ui/Badge'
import { Spinner } from './ui/Spinner'
import { formatBB, profitColor } from '../lib/utils'
import type { HandFilters } from '../types'

const POSITIONS = ['BTN', 'CO', 'HJ', 'MP', 'UTG', 'UTG+1', 'SB', 'BB']

export function HandBrowser() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<HandFilters>({ page: 1, limit: 50 })
  const [showFilters, setShowFilters] = useState(false)

  const { data: hands, isLoading } = useHands(filters)

  const setFilter = <K extends keyof HandFilters>(key: K, value: HandFilters[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }))
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold text-zinc-100">Handen</h1>
        <button
          onClick={() => setShowFilters((v) => !v)}
          className="flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-100 bg-zinc-800 px-3 py-1.5 rounded-lg"
        >
          <SlidersHorizontal className="w-4 h-4" />
          Filters
        </button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 mb-4 grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <label className="text-xs text-zinc-500 mb-1 block">Positie</label>
            <select
              className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 rounded px-2 py-1.5 text-sm"
              value={filters.position ?? ''}
              onChange={(e) => setFilter('position', e.target.value || undefined)}
            >
              <option value="">Alle posities</option>
              {POSITIONS.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>

          <div>
            <label className="text-xs text-zinc-500 mb-1 block">Fast Fold</label>
            <select
              className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 rounded px-2 py-1.5 text-sm"
              value={filters.is_fast_fold === undefined ? '' : String(filters.is_fast_fold)}
              onChange={(e) => {
                const v = e.target.value
                setFilter('is_fast_fold', v === '' ? undefined : v === 'true')
              }}
            >
              <option value="">Beide</option>
              <option value="false">Uitgespeeld</option>
              <option value="true">Fast Fold</option>
            </select>
          </div>

          <div>
            <label className="text-xs text-zinc-500 mb-1 block">Street bereikt</label>
            <select
              className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 rounded px-2 py-1.5 text-sm"
              value={filters.street_reached ?? ''}
              onChange={(e) => setFilter('street_reached', e.target.value || undefined)}
            >
              <option value="">Alle</option>
              <option value="flop">Flop+</option>
              <option value="turn">Turn+</option>
              <option value="river">River+</option>
              <option value="showdown">Showdown</option>
            </select>
          </div>

          <div>
            <label className="text-xs text-zinc-500 mb-1 block">Min winst (BB)</label>
            <input
              type="number"
              className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 rounded px-2 py-1.5 text-sm"
              placeholder="b.v. -10"
              value={filters.min_profit ?? ''}
              onChange={(e) => setFilter('min_profit', e.target.value ? Number(e.target.value) : undefined)}
            />
          </div>
        </div>
      )}

      {/* Table */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-500 text-xs uppercase tracking-wider">
              <th className="text-left px-4 py-3">Datum</th>
              <th className="text-left px-4 py-3">Stakes</th>
              <th className="text-left px-4 py-3">Pos</th>
              <th className="text-left px-4 py-3">Kaarten</th>
              <th className="text-left px-4 py-3">Flop</th>
              <th className="text-right px-4 py-3">Winst/Verlies</th>
              <th className="text-left px-4 py-3">Tags</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={7} className="text-center py-12">
                  <Spinner />
                </td>
              </tr>
            ) : !hands?.length ? (
              <tr>
                <td colSpan={7} className="text-center py-12 text-zinc-600">
                  Geen handen gevonden
                </td>
              </tr>
            ) : (
              hands.map((hand) => (
                <tr
                  key={hand.id}
                  className="border-b border-zinc-800/50 hover:bg-zinc-800/50 cursor-pointer transition-colors"
                  onClick={() => navigate(`/hands/${hand.id}`)}
                >
                  <td className="px-4 py-2.5 text-zinc-400">
                    {new Date(hand.played_at).toLocaleDateString('nl-NL', {
                      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
                    })}
                  </td>
                  <td className="px-4 py-2.5 text-zinc-300">${hand.stakes_bb.toFixed(2)}</td>
                  <td className="px-4 py-2.5">
                    <span className="text-xs font-mono bg-zinc-800 px-1.5 py-0.5 rounded text-zinc-300">
                      {hand.hero_position ?? '?'}
                    </span>
                  </td>
                  <td className="px-4 py-2.5">
                    <HoleCards cards={hand.hero_cards} />
                  </td>
                  <td className="px-4 py-2.5 text-zinc-500 text-xs font-mono">
                    {hand.flop_cards ?? '—'}
                  </td>
                  <td className={`px-4 py-2.5 text-right font-mono font-medium ${profitColor(hand.hero_profit_bb)}`}>
                    {formatBB(hand.hero_profit_bb)}
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex gap-1 flex-wrap">
                      {hand.is_fast_fold && <Badge variant="default">FF</Badge>}
                      {hand.run_it_twice && <Badge variant="blue">RIT</Badge>}
                      {hand.hero_pfr && <Badge variant="amber">PFR</Badge>}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-3 text-sm">
        <span className="text-zinc-500">{hands?.length ?? 0} handen weergegeven</span>
        <div className="flex gap-2">
          <button
            className="flex items-center gap-1 px-3 py-1.5 bg-zinc-800 text-zinc-300 rounded hover:bg-zinc-700 disabled:opacity-40"
            onClick={() => setFilter('page', filters.page - 1)}
            disabled={filters.page <= 1 || isLoading}
          >
            <ChevronLeft className="w-4 h-4" /> Vorige
          </button>
          <span className="px-3 py-1.5 text-zinc-500">Pagina {filters.page}</span>
          <button
            className="flex items-center gap-1 px-3 py-1.5 bg-zinc-800 text-zinc-300 rounded hover:bg-zinc-700 disabled:opacity-40"
            onClick={() => setFilter('page', filters.page + 1)}
            disabled={!hands?.length || hands.length < filters.limit || isLoading}
          >
            Volgende <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
