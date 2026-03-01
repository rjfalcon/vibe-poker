import client from './client'
import type { ImportSession } from '../types'

export async function listSessions(): Promise<ImportSession[]> {
  const { data } = await client.get<ImportSession[]>('/sessions/')
  return data
}

export interface BulkImportResult {
  total_hands: number
  session_count: number
  sessions: ImportSession[]
}

export async function importFiles(files: File[]): Promise<BulkImportResult> {
  const form = new FormData()
  for (const file of files) {
    form.append('files', file)
  }
  const { data } = await client.post<BulkImportResult>('/sessions/import', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function deleteSession(id: string): Promise<void> {
  await client.delete(`/sessions/${id}`)
}
