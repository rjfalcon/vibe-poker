import { useQuery } from '@tanstack/react-query'
import { getHand, listHands } from '../api/hands'
import { listSessions } from '../api/sessions'
import type { HandFilters } from '../types'

export function useHands(filters: HandFilters) {
  return useQuery({
    queryKey: ['hands', filters],
    queryFn: () => listHands(filters),
  })
}

export function useHand(id: string | undefined) {
  return useQuery({
    queryKey: ['hand', id],
    queryFn: () => getHand(id!),
    enabled: !!id,
  })
}

export function useSessions() {
  return useQuery({
    queryKey: ['sessions'],
    queryFn: listSessions,
  })
}
