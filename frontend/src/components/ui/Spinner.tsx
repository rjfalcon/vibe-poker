import { cn } from '../../lib/utils'

export function Spinner({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        'inline-block w-5 h-5 border-2 border-zinc-600 border-t-green-500 rounded-full animate-spin',
        className,
      )}
    />
  )
}
