import client from './client'

export interface StreetAnalysis {
  beoordeling: 'goed' | 'acceptabel' | 'fout'
  uitleg: string
}

export interface Fout {
  straat: string
  moment: string
  probleem: string
  beter: string
}

export interface HandAnalysis {
  samenvatting: string
  straten: Partial<Record<string, StreetAnalysis>>
  fouten: Fout[]
  score: number
  conclusie: string
}

export async function analyzeHand(handId: string): Promise<HandAnalysis> {
  const { data } = await client.post<HandAnalysis>(`/hands/${handId}/analyze`)
  return data
}

export interface Leak {
  categorie: string
  ernst: 'major' | 'minor'
  stat: string
  beschrijving: string
  advies: string
}

export interface SterkPunt {
  categorie: string
  beschrijving: string
}

export interface BulkAnalysis {
  total_hands: number
  hands_analyzed: number
  overall_score: number | null
  winrate_bb100: number
  leaks: Leak[]
  sterke_punten: SterkPunt[]
  samenvatting: string
  conclusie: string
}

export async function analyzeBulk(sessionId?: string): Promise<BulkAnalysis> {
  const params = sessionId ? { session_id: sessionId } : {}
  const { data } = await client.get<BulkAnalysis>('/stats/bulk-analysis', { params })
  return data
}
