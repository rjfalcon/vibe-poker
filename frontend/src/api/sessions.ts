import client from './client'
import type { ImportSession } from '../types'

export async function listSessions(): Promise<ImportSession[]> {
  const { data } = await client.get<ImportSession[]>('/sessions/')
  return data
}

export async function importFile(file: File): Promise<ImportSession> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await client.post<ImportSession>('/sessions/import', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function deleteSession(id: string): Promise<void> {
  await client.delete(`/sessions/${id}`)
}
