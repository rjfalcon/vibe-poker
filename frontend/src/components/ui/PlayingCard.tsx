import { parseCard, suitColor } from '../../lib/utils'
import { cn } from '../../lib/utils'

const SUIT_SYMBOLS: Record<string, string> = { h: '♥', d: '♦', c: '♣', s: '♠' }

interface PlayingCardProps {
  card: string
  size?: 'sm' | 'md'
  className?: string
}

export function PlayingCard({ card, size = 'sm', className }: PlayingCardProps) {
  const parsed = parseCard(card)
  if (!parsed) return null

  const { rank, suit } = parsed
  const color = suitColor(suit)
  const symbol = SUIT_SYMBOLS[suit] ?? suit

  return (
    <span
      className={cn(
        'inline-flex items-center justify-center font-bold rounded bg-zinc-100 text-zinc-900 leading-none select-none',
        size === 'sm' ? 'w-7 h-9 text-sm' : 'w-10 h-13 text-base',
        className,
      )}
    >
      <span className={cn('flex flex-col items-center', color)}>
        <span>{rank}</span>
        <span className="text-xs">{symbol}</span>
      </span>
    </span>
  )
}

export function HoleCards({ cards, className }: { cards: string | null; className?: string }) {
  if (!cards) return <span className="text-zinc-600 text-sm">??</span>
  const cardList = cards.split(' ')
  return (
    <div className={cn('flex gap-1', className)}>
      {cardList.map((c, i) => <PlayingCard key={i} card={c} />)}
    </div>
  )
}
