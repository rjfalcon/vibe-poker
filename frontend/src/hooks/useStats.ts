import { useQuery } from '@tanstack/react-query'
import { getOverviewStats, getPositionStats, getTimeline } from '../api/stats'

export function useOverviewStats(sessionId?: string) {
  return useQuery({
    queryKey: ['stats', 'overview', sessionId],
    queryFn: () => getOverviewStats(sessionId),
  })
}

export function usePositionStats(sessionId?: string) {
  return useQuery({
    queryKey: ['stats', 'positions', sessionId],
    queryFn: () => getPositionStats(sessionId),
  })
}

export function useTimeline(sessionId?: string) {
  return useQuery({
    queryKey: ['stats', 'timeline', sessionId],
    queryFn: () => getTimeline(sessionId),
  })
}
