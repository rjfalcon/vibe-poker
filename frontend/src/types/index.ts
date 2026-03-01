export interface ImportSession {
  id: string
  filename: string
  imported_at: string
  hero_name: string | null
  hand_count: number
}

export interface HandSummary {
  id: string
  ggpoker_hand_id: string
  played_at: string
  stakes_bb: number
  table_name: string
  hero_position: string | null
  hero_cards: string | null
  is_fast_fold: boolean
  hero_vpip: boolean
  hero_pfr: boolean
  hero_profit_bb: number
  flop_cards: string | null
  run_it_twice: boolean
}

export interface PlayerOut {
  seat: number
  name: string
  stack_bb: number
  position: string | null
  is_hero: boolean
  hole_cards: string | null
  profit_bb: number
}

export interface ActionOut {
  player_name: string
  street: string
  sequence: number
  action_type: string
  amount_bb: number | null
  is_all_in: boolean
}

export interface HandDetail extends HandSummary {
  hero_went_to_showdown: boolean
  hero_won_at_showdown: boolean
  hero_had_3bet_opportunity: boolean
  hero_3bet: boolean
  turn_card: string | null
  river_card: string | null
  rake_bb: number
  players: PlayerOut[]
  actions: ActionOut[]
}

export interface OverviewStats {
  total_hands: number
  hands_played_out: number
  hands_fast_folded: number
  fast_fold_pct: number
  vpip: number
  pfr: number
  three_bet_pct: number
  af: number
  wtsd: number
  wsd: number
  bb_per_100: number
  total_profit_bb: number
  rake_bb: number
}

export interface PositionStats {
  position: string
  hands: number
  vpip: number
  pfr: number
  three_bet_pct: number
  bb_per_100: number
  total_profit_bb: number
}

export interface TimelinePoint {
  index: number
  played_at: string
  cumulative_bb: number
  bb_per_100: number
}

export interface HandFilters {
  session_id?: string
  position?: string
  is_fast_fold?: boolean
  min_profit?: number
  max_profit?: number
  street_reached?: string
  page: number
  limit: number
}
