import client from './client'
import type { OverviewStats, PositionStats, TimelinePoint } from '../types'

export async function getOverviewStats(sessionId?: string): Promise<OverviewStats> {
  const { data } = await client.get<OverviewStats>('/stats/overview', {
    params: sessionId ? { session_id: sessionId } : {},
  })
  return data
}

export async function getPositionStats(sessionId?: string): Promise<PositionStats[]> {
  const { data } = await client.get<PositionStats[]>('/stats/positions', {
    params: sessionId ? { session_id: sessionId } : {},
  })
  return data
}

export async function getTimeline(sessionId?: string, sampleEvery = 10): Promise<TimelinePoint[]> {
  const { data } = await client.get<TimelinePoint[]>('/stats/timeline', {
    params: { sample_every: sampleEvery, ...(sessionId ? { session_id: sessionId } : {}) },
  })
  return data
}
