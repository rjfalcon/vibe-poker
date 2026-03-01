import client from './client'
import type { HandDetail, HandFilters, HandSummary } from '../types'

export async function listHands(filters: HandFilters): Promise<HandSummary[]> {
  const params: Record<string, string | number | boolean> = {
    page: filters.page,
    limit: filters.limit,
  }
  if (filters.session_id) params.session_id = filters.session_id
  if (filters.position) params.position = filters.position
  if (filters.is_fast_fold !== undefined) params.is_fast_fold = filters.is_fast_fold
  if (filters.min_profit !== undefined) params.min_profit = filters.min_profit
  if (filters.max_profit !== undefined) params.max_profit = filters.max_profit
  if (filters.street_reached) params.street_reached = filters.street_reached

  const { data } = await client.get<HandSummary[]>('/hands/', { params })
  return data
}

export async function getHand(id: string): Promise<HandDetail> {
  const { data } = await client.get<HandDetail>(`/hands/${id}`)
  return data
}

export async function getReplay(id: string) {
  const { data } = await client.get(`/hands/${id}/replay`)
  return data
}
