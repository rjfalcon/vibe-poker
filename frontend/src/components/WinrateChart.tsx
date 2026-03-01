import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts'
import { Card, CardHeader, CardTitle } from './ui/Card'
import { Spinner } from './ui/Spinner'
import type { TimelinePoint } from '../types'

interface Props {
  data: TimelinePoint[] | undefined
  isLoading: boolean
}

export function WinrateChart({ data, isLoading }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Winrate over tijd (cumulatief BB)</CardTitle>
      </CardHeader>

      {isLoading ? (
        <div className="flex items-center justify-center h-48"><Spinner /></div>
      ) : !data?.length ? (
        <div className="flex items-center justify-center h-48 text-zinc-600 text-sm">
          Geen data beschikbaar
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
            <XAxis
              dataKey="index"
              tick={{ fill: '#71717a', fontSize: 11 }}
              tickLine={false}
              label={{ value: 'Handen', position: 'insideBottom', offset: -2, fill: '#52525b', fontSize: 11 }}
            />
            <YAxis
              tick={{ fill: '#71717a', fontSize: 11 }}
              tickLine={false}
              tickFormatter={(v: number) => `${v}BB`}
              width={52}
            />
            <Tooltip
              contentStyle={{ background: '#18181b', border: '1px solid #3f3f46', borderRadius: 8 }}
              labelStyle={{ color: '#a1a1aa', fontSize: 11 }}
              formatter={(v: number) => [`${v.toFixed(1)} BB`, 'Cumulatief']}
            />
            <ReferenceLine y={0} stroke="#3f3f46" />
            <Line
              type="monotone"
              dataKey="cumulative_bb"
              stroke="#22c55e"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#22c55e' }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Card>
  )
}
