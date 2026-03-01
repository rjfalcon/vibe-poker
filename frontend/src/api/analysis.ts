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
