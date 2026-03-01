import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, BrainCircuit } from 'lucide-react'
import { useHand } from '../hooks/useHands'
import { analyzeHand } from '../api/analysis'
import type { HandAnalysis } from '../api/analysis'
import { HoleCards, PlayingCard } from './ui/PlayingCard'
import { Badge } from './ui/Badge'
import { Card } from './ui/Card'
import { Spinner } from './ui/Spinner'
import { formatAction, actionColor, formatBB, profitColor } from '../lib/utils'
import type { ActionOut } from '../types'

const STREETS = ['PREFLOP', 'FLOP', 'TURN', 'RIVER'] as const

const BEOORDELING_STYLE: Record<string, string> = {
  goed:        'bg-green-900/40 text-green-400 border-green-800',
  acceptabel:  'bg-amber-900/40 text-amber-400 border-amber-800',
  fout:        'bg-red-900/40 text-red-400 border-red-800',
}

function ScoreBadge({ score }: { score: number }) {
  const color = score >= 8 ? 'text-green-400' : score >= 5 ? 'text-amber-400' : 'text-red-400'
  return (
    <div className="flex items-center gap-1.5">
      <span className={`text-3xl font-bold ${color}`}>{score}</span>
      <span className="text-zinc-500 text-sm">/10</span>
    </div>
  )
}

function AnalysisPanel({ analysis, onReset }: { analysis: HandAnalysis; onReset: () => void }) {
  return (
    <div className="bg-violet-950/30 border border-violet-800/50 rounded-2xl p-5 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-5 h-5 text-violet-400" />
          <span className="text-sm font-semibold text-violet-300">AI Analyse</span>
        </div>
        <div className="flex items-center gap-4">
          <ScoreBadge score={analysis.score} />
          <button onClick={onReset} className="text-xs text-zinc-500 hover:text-zinc-300 underline">
            verwijder
          </button>
        </div>
      </div>

      {/* Samenvatting */}
      <p className="text-sm text-zinc-300 leading-relaxed">{analysis.samenvatting}</p>

      {/* Per street */}
      {Object.entries(analysis.straten).length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-zinc-500 uppercase tracking-wider">Per straat</p>
          {Object.entries(analysis.straten).map(([street, s]) => {
            if (!s) return null
            const style = BEOORDELING_STYLE[s.beoordeling] ?? BEOORDELING_STYLE.acceptabel
            return (
              <div key={street} className={`border rounded-lg px-4 py-3 ${style}`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-bold uppercase tracking-wider">{street}</span>
                  <span className="text-xs px-1.5 py-0.5 rounded bg-black/20 capitalize">
                    {s.beoordeling}
                  </span>
                </div>
                <p className="text-sm opacity-90 leading-relaxed">{s.uitleg}</p>
              </div>
            )
          })}
        </div>
      )}

      {/* Fouten */}
      {analysis.fouten.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-zinc-500 uppercase tracking-wider">
            Verbeterpunten ({analysis.fouten.length})
          </p>
          {analysis.fouten.map((f, i) => (
            <div key={i} className="bg-red-950/30 border border-red-800/50 rounded-lg px-4 py-3 space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-red-400 uppercase">{f.straat}</span>
                <span className="text-xs text-zinc-400">{f.moment}</span>
              </div>
              <p className="text-sm text-red-300"><span className="font-medium">Probleem:</span> {f.probleem}</p>
              <p className="text-sm text-green-300"><span className="font-medium">Beter:</span> {f.beter}</p>
            </div>
          ))}
        </div>
      )}

      {/* Conclusie */}
      <div className="border-t border-violet-800/30 pt-4">
        <p className="text-sm text-violet-200 leading-relaxed italic">{analysis.conclusie}</p>
      </div>
    </div>
  )
}

export function HandDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: hand, isLoading, isError } = useHand(id)
  const [analysis, setAnalysis] = useState<HandAnalysis | null>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [analyzeError, setAnalyzeError] = useState<string | null>(null)

  async function handleAnalyze() {
    if (!id) return
    setAnalyzing(true)
    setAnalyzeError(null)
    try {
      const result = await analyzeHand(id)
      setAnalysis(result)
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setAnalyzeError(msg ?? 'Analyse mislukt')
    } finally {
      setAnalyzing(false)
    }
  }

  if (isLoading) return <div className="flex items-center justify-center h-64"><Spinner /></div>
  if (isError || !hand) return <div className="p-6 text-red-400">Hand niet gevonden</div>

  const actionsByStreet = (street: string): ActionOut[] =>
    hand.actions.filter((a) => a.street === street)

  const board: string[] = [
    ...(hand.flop_cards?.split(' ') ?? []),
    ...(hand.turn_card ? [hand.turn_card] : []),
    ...(hand.river_card ? [hand.river_card] : []),
  ]

  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-1.5 text-zinc-500 hover:text-zinc-300 text-sm mb-3"
          >
            <ArrowLeft className="w-4 h-4" /> Terug
          </button>
          <h1 className="text-lg font-bold text-zinc-100">Hand #{hand.ggpoker_hand_id}</h1>
          <p className="text-sm text-zinc-500 mt-0.5">
            {new Date(hand.played_at).toLocaleString('nl-NL')} · {hand.table_name} · ${hand.stakes_bb.toFixed(2)} BB
          </p>
        </div>

        <div className="flex flex-col items-end gap-2">
          <span className={`text-2xl font-bold ${profitColor(hand.hero_profit_bb)}`}>
            {formatBB(hand.hero_profit_bb)}
          </span>
          <div className="flex gap-1.5">
            {hand.is_fast_fold && <Badge>Fast Fold</Badge>}
            {hand.run_it_twice && <Badge variant="blue">Run It Twice</Badge>}
            {hand.hero_went_to_showdown && (
              <Badge variant={hand.hero_won_at_showdown ? 'green' : 'red'}>
                {hand.hero_won_at_showdown ? 'Gewonnen' : 'Verloren'} SD
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Hero hand info */}
      <Card className="flex items-center gap-6">
        <div>
          <p className="text-xs text-zinc-500 mb-1">Positie</p>
          <span className="text-lg font-bold text-zinc-100">{hand.hero_position ?? '?'}</span>
        </div>
        <div>
          <p className="text-xs text-zinc-500 mb-1">Kaarten</p>
          <HoleCards cards={hand.hero_cards} />
        </div>
        {board.length > 0 && (
          <div>
            <p className="text-xs text-zinc-500 mb-1">Board</p>
            <div className="flex gap-1">
              {board.map((c, i) => <PlayingCard key={i} card={c} />)}
            </div>
          </div>
        )}
        <div className="ml-auto">
          <p className="text-xs text-zinc-500 mb-1">Rake</p>
          <span className="text-red-400">{hand.rake_bb.toFixed(2)} BB</span>
        </div>
      </Card>

      {/* Players */}
      <Card>
        <p className="text-xs text-zinc-500 uppercase tracking-wider mb-3">Spelers</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {hand.players.map((p) => (
            <div
              key={p.seat}
              className={`flex items-center justify-between px-3 py-2 rounded-lg ${p.is_hero ? 'bg-green-900/30 border border-green-800' : 'bg-zinc-800/50'}`}
            >
              <div>
                <span className="text-xs text-zinc-500 mr-1.5">{p.position}</span>
                <span className={`text-sm ${p.is_hero ? 'text-green-400 font-medium' : 'text-zinc-300'}`}>
                  {p.name}
                </span>
              </div>
              <div className="text-right">
                <p className="text-xs text-zinc-500">{p.stack_bb.toFixed(1)}BB</p>
                {p.hole_cards && <p className="text-xs text-zinc-400 font-mono">{p.hole_cards}</p>}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* AI Analysis button */}
      {!analysis && (
        <div>
          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="flex items-center gap-2 px-4 py-2 bg-violet-700 hover:bg-violet-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
          >
            <BrainCircuit className="w-4 h-4" />
            {analyzing ? 'Claude analyseert...' : 'Analyseer met AI'}
          </button>
          {analyzeError && (
            <p className="mt-2 text-sm text-red-400">{analyzeError}</p>
          )}
        </div>
      )}

      {/* AI Analysis results */}
      {analysis && <AnalysisPanel analysis={analysis} onReset={() => setAnalysis(null)} />}

      {/* Street-by-street actions */}
      <div className="space-y-3">
        {STREETS.map((street) => {
          const acts = actionsByStreet(street)
          if (!acts.length && street !== 'PREFLOP') return null
          const streetBoard = street === 'FLOP' ? hand.flop_cards?.split(' ') ?? []
            : street === 'TURN' ? (hand.turn_card ? [hand.turn_card] : [])
            : street === 'RIVER' ? (hand.river_card ? [hand.river_card] : [])
            : []

          return (
            <Card key={street}>
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">{street}</span>
                {streetBoard.length > 0 && (
                  <div className="flex gap-1">
                    {streetBoard.map((c, i) => <PlayingCard key={i} card={c} size="sm" />)}
                  </div>
                )}
              </div>
              {acts.length === 0 ? (
                <p className="text-zinc-600 text-sm italic">Geen acties</p>
              ) : (
                <div className="space-y-1">
                  {acts.map((a, i) => {
                    const isHero = a.player_name === hand.players.find((p) => p.is_hero)?.name
                    return (
                      <div
                        key={i}
                        className={`flex items-center gap-2 text-sm ${isHero ? 'font-medium' : ''}`}
                      >
                        <span className={`w-28 truncate ${isHero ? 'text-green-400' : 'text-zinc-400'}`}>
                          {a.player_name}
                        </span>
                        <span className={actionColor(a.action_type)}>
                          {formatAction(a.action_type, a.amount_bb)}
                        </span>
                        {a.is_all_in && (
                          <Badge variant="red">All-in</Badge>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}
