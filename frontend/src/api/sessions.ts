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

const BATCH_SIZE = 5

async function importBatch(files: File[]): Promise<BulkImportResult> {
  const form = new FormData()
  for (const file of files) {
    form.append('files', file)
  }
  const { data } = await client.post<BulkImportResult>('/sessions/import', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function importFiles(
  files: File[],
  onProgress?: (done: number, total: number) => void,
): Promise<BulkImportResult> {
  const result: BulkImportResult = { total_hands: 0, session_count: 0, sessions: [] }

  for (let i = 0; i < files.length; i += BATCH_SIZE) {
    const batch = files.slice(i, i + BATCH_SIZE)
    const batchResult = await importBatch(batch)
    result.total_hands += batchResult.total_hands
    result.session_count += batchResult.session_count
    result.sessions.push(...batchResult.sessions)
    onProgress?.(Math.min(i + BATCH_SIZE, files.length), files.length)
  }

  return result
}

export async function deleteSession(id: string): Promise<void> {
  await client.delete(`/sessions/${id}`)
}
