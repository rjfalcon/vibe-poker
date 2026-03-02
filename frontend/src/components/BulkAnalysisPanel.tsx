import { useState } from 'react'
import { BrainCircuit, TrendingUp, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react'
import { analyzeBulk } from '../api/analysis'
import type { BulkAnalysis, Leak, SterkPunt } from '../api/analysis'
import { Spinner } from './ui/Spinner'

function ScoreBadge({ score }: { score: number }) {
  const color = score >= 8 ? 'text-green-400' : score >= 5 ? 'text-amber-400' : 'text-red-400'
  return (
    <div className="flex items-center gap-1.5">
      <span className={`text-3xl font-bold ${color}`}>{score}</span>
      <span className="text-zinc-500 text-sm">/10</span>
    </div>
  )
}

function LeakCard({ leak }: { leak: Leak }) {
  const [open, setOpen] = useState(false)
  const isMajor = leak.ernst === 'major'
  const borderColor = isMajor ? 'border-red-800' : 'border-amber-800'
  const bgColor = isMajor ? 'bg-red-950/30' : 'bg-amber-950/30'
  const badgeColor = isMajor ? 'bg-red-900/60 text-red-300' : 'bg-amber-900/60 text-amber-300'
  const statColor = isMajor ? 'text-red-400' : 'text-amber-400'

  return (
    <div className={`border rounded-lg px-4 py-3 ${bgColor} ${borderColor}`}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between gap-2 text-left"
      >
        <div className="flex items-center gap-2 min-w-0">
          <span className={`text-xs px-1.5 py-0.5 rounded font-medium shrink-0 ${badgeColor}`}>
            {isMajor ? 'Major' : 'Minor'}
          </span>
          <span className="text-sm font-medium text-zinc-200 truncate">{leak.categorie}</span>
          <span className={`text-xs font-mono shrink-0 ${statColor}`}>{leak.stat}</span>
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-zinc-500 shrink-0" /> : <ChevronDown className="w-4 h-4 text-zinc-500 shrink-0" />}
      </button>
      {open && (
        <div className="mt-3 space-y-2 border-t border-white/10 pt-3">
          <p className="text-sm text-zinc-300 leading-relaxed">{leak.beschrijving}</p>
          <p className="text-sm text-green-300">
            <span className="font-medium">Advies: </span>{leak.advies}
          </p>
        </div>
      )}
    </div>
  )
}

function SterkPuntCard({ punt }: { punt: SterkPunt }) {
  return (
    <div className="bg-green-950/30 border border-green-800/50 rounded-lg px-4 py-3">
      <div className="flex items-center gap-2 mb-1">
        <TrendingUp className="w-3.5 h-3.5 text-green-400 shrink-0" />
        <span className="text-xs font-bold text-green-400 uppercase tracking-wider">{punt.categorie}</span>
      </div>
      <p className="text-sm text-green-200 leading-relaxed">{punt.beschrijving}</p>
    </div>
  )
}

function AnalysisResult({ analysis, onReset }: { analysis: BulkAnalysis; onReset: () => void }) {
  const majorLeaks = analysis.leaks.filter(l => l.ernst === 'major')
  const minorLeaks = analysis.leaks.filter(l => l.ernst === 'minor')

  return (
    <div className="bg-violet-950/30 border border-violet-800/50 rounded-2xl p-5 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-5 h-5 text-violet-400" />
          <span className="text-sm font-semibold text-violet-300">Spel Analyse</span>
          <span className="text-xs text-zinc-500">
            {analysis.total_hands} handen · {analysis.hands_analyzed} uitgespeeld
          </span>
        </div>
        <div className="flex items-center gap-4">
          {analysis.overall_score !== null && <ScoreBadge score={analysis.overall_score} />}
          <button onClick={onReset} className="text-xs text-zinc-500 hover:text-zinc-300 underline">
            verwijder
          </button>
        </div>
      </div>

      {/* Samenvatting */}
      <p className="text-sm text-zinc-300 leading-relaxed">{analysis.samenvatting}</p>

      {/* Leaks */}
      {analysis.leaks.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
            <p className="text-xs text-zinc-500 uppercase tracking-wider">
              Leaks ({majorLeaks.length} major · {minorLeaks.length} minor)
            </p>
          </div>
          {/* Major first */}
          {[...majorLeaks, ...minorLeaks].map((leak, i) => (
            <LeakCard key={i} leak={leak} />
          ))}
        </div>
      )}

      {/* Sterke punten */}
      {analysis.sterke_punten.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-zinc-500 uppercase tracking-wider">Sterke punten</p>
          {analysis.sterke_punten.map((punt, i) => (
            <SterkPuntCard key={i} punt={punt} />
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

export function BulkAnalysisPanel() {
  const [analysis, setAnalysis] = useState<BulkAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleAnalyze() {
    setLoading(true)
    setError(null)
    try {
      const result = await analyzeBulk()
      setAnalysis(result)
    } catch {
      setError('Analyse mislukt. Probeer opnieuw.')
    } finally {
      setLoading(false)
    }
  }

  if (analysis) {
    return <AnalysisResult analysis={analysis} onReset={() => setAnalysis(null)} />
  }

  return (
    <div>
      <button
        onClick={handleAnalyze}
        disabled={loading}
        className="flex items-center gap-2 px-4 py-2 bg-violet-700 hover:bg-violet-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
      >
        {loading ? <Spinner className="w-4 h-4" /> : <BrainCircuit className="w-4 h-4" />}
        {loading ? 'Analyseren...' : 'Analyseer mijn spel'}
      </button>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
    </div>
  )
}
