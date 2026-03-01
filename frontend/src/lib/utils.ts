import { clsx, type ClassValue } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatBB(bb: number, decimals = 1): string {
  const sign = bb > 0 ? '+' : ''
  return `${sign}${bb.toFixed(decimals)} BB`
}

export function formatPct(value: number): string {
  return `${value.toFixed(1)}%`
}

export function profitColor(bb: number): string {
  if (bb > 0) return 'text-green-400'
  if (bb < 0) return 'text-red-400'
  return 'text-zinc-400'
}

export function actionColor(actionType: string): string {
  switch (actionType) {
    case 'RAISE': return 'text-amber-400'
    case 'BET': return 'text-amber-400'
    case 'CALL': return 'text-blue-400'
    case 'CHECK': return 'text-zinc-400'
    case 'FOLD': return 'text-zinc-500'
    case 'FAST_FOLD': return 'text-zinc-600'
    default: return 'text-zinc-400'
  }
}

export function formatAction(type: string, amountBb: number | null): string {
  if (type === 'FOLD') return 'folds'
  if (type === 'FAST_FOLD') return 'folds [Fast Fold]'
  if (type === 'CHECK') return 'checks'
  if (type === 'CALL') return amountBb ? `calls ${amountBb.toFixed(1)}BB` : 'calls'
  if (type === 'BET') return amountBb ? `bets ${amountBb.toFixed(1)}BB` : 'bets'
  if (type === 'RAISE') return amountBb ? `raises to ${amountBb.toFixed(1)}BB` : 'raises'
  return type.toLowerCase()
}

export function suitColor(suit: string): string {
  return suit === 'h' || suit === 'd' ? 'text-red-500' : 'text-zinc-100'
}

export function parseCard(card: string): { rank: string; suit: string } | null {
  if (!card || card.length < 2) return null
  return { rank: card.slice(0, -1), suit: card.slice(-1) }
}
