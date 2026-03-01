import { cn } from '../../lib/utils'

interface CardProps {
  className?: string
  children: React.ReactNode
}

export function Card({ className, children }: CardProps) {
  return (
    <div className={cn('bg-zinc-900 border border-zinc-800 rounded-xl p-4', className)}>
      {children}
    </div>
  )
}

export function CardHeader({ className, children }: CardProps) {
  return <div className={cn('mb-3', className)}>{children}</div>
}

export function CardTitle({ className, children }: CardProps) {
  return <h3 className={cn('text-sm font-medium text-zinc-400 uppercase tracking-wider', className)}>{children}</h3>
}
