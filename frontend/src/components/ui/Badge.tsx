import { cn } from '../../lib/utils'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'green' | 'red' | 'amber' | 'blue'
  className?: string
}

const variants = {
  default: 'bg-zinc-800 text-zinc-300',
  green: 'bg-green-900/50 text-green-400 border border-green-800',
  red: 'bg-red-900/50 text-red-400 border border-red-800',
  amber: 'bg-amber-900/50 text-amber-400 border border-amber-800',
  blue: 'bg-blue-900/50 text-blue-400 border border-blue-800',
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded text-xs font-medium', variants[variant], className)}>
      {children}
    </span>
  )
}
