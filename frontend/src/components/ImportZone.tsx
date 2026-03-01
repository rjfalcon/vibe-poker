import { useCallback, useRef, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckCircle, Upload, XCircle } from 'lucide-react'
import { importFiles } from '../api/sessions'
import { Spinner } from './ui/Spinner'
import { cn } from '../lib/utils'

export function ImportZone() {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const qc = useQueryClient()

  const { mutate, isPending, isSuccess, isError, error, reset, data } = useMutation({
    mutationFn: importFiles,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['sessions'] })
      qc.invalidateQueries({ queryKey: ['stats'] })
      qc.invalidateQueries({ queryKey: ['hands'] })
    },
  })

  const handleFiles = useCallback(
    (fileList: FileList | null) => {
      if (!fileList?.length) return
      const txtFiles = Array.from(fileList).filter((f) => f.name.endsWith('.txt'))
      if (!txtFiles.length) {
        alert('Alleen .txt bestanden worden ondersteund')
        return
      }
      reset()
      mutate(txtFiles)
    },
    [mutate, reset],
  )

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold text-zinc-100 mb-6">Hand History Importeren</h1>

      {/* Drop zone */}
      <div
        className={cn(
          'relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-colors',
          dragging
            ? 'border-green-500 bg-green-900/10'
            : 'border-zinc-700 hover:border-zinc-500 bg-zinc-900/50',
        )}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files) }}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".txt"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />

        {isPending ? (
          <div className="flex flex-col items-center gap-3">
            <Spinner className="w-8 h-8" />
            <p className="text-zinc-400">Importeren...</p>
          </div>
        ) : isSuccess ? (
          <div className="flex flex-col items-center gap-3 text-green-400">
            <CheckCircle className="w-10 h-10" />
            <p className="font-medium">{data.total_hands} handen geïmporteerd</p>
            <p className="text-sm text-zinc-400">
              {data.session_count} {data.session_count === 1 ? 'bestand' : 'bestanden'}
            </p>
            {data.session_count > 1 && (
              <ul className="mt-1 text-xs text-zinc-500 space-y-0.5">
                {data.sessions.map((s) => (
                  <li key={s.id}>{s.filename} — {s.hand_count} handen</li>
                ))}
              </ul>
            )}
          </div>
        ) : isError ? (
          <div className="flex flex-col items-center gap-3 text-red-400">
            <XCircle className="w-10 h-10" />
            <p className="font-medium">Import mislukt</p>
            <p className="text-sm text-zinc-500">
              {(error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Onbekende fout'}
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3 text-zinc-400">
            <Upload className="w-10 h-10" />
            <p className="text-lg font-medium text-zinc-300">Sleep .txt bestanden hierheen</p>
            <p className="text-sm">of klik om te bladeren — meerdere bestanden tegelijk mogelijk</p>
            <p className="text-xs text-zinc-600 mt-2">GGPoker Rush & Cash hand history export</p>
          </div>
        )}
      </div>

      {/* Reset na succes */}
      {(isSuccess || isError) && (
        <button
          onClick={reset}
          className="mt-4 text-sm text-zinc-500 hover:text-zinc-300 underline"
        >
          Meer bestanden importeren
        </button>
      )}

      {/* Instructies */}
      <div className="mt-8 bg-zinc-900 border border-zinc-800 rounded-xl p-5">
        <h2 className="text-sm font-semibold text-zinc-300 mb-3">Hoe exporteer je vanuit GGPoker?</h2>
        <ol className="text-sm text-zinc-400 space-y-1.5 list-decimal list-inside">
          <li>Open GGPoker client → <span className="text-zinc-300">Menu → Hand History</span></li>
          <li>Selecteer de gewenste periode en tabeltype <span className="text-zinc-300">Rush & Cash</span></li>
          <li>Klik op <span className="text-zinc-300">Export</span> en sla op als <code className="text-green-400">.txt</code></li>
          <li>Sleep één of meerdere bestanden naar bovenstaand veld</li>
        </ol>
      </div>
    </div>
  )
}
