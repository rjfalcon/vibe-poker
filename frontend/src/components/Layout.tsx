import { NavLink, Outlet } from 'react-router-dom'
import { BarChart2, BookOpen, Grid, Upload } from 'lucide-react'
import { cn } from '../lib/utils'

const NAV = [
  { to: '/', icon: Grid, label: 'Dashboard' },
  { to: '/hands', icon: BookOpen, label: 'Handen' },
  { to: '/positions', icon: BarChart2, label: 'Positie' },
  { to: '/import', icon: Upload, label: 'Import' },
]

export function Layout() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-52 flex-shrink-0 bg-zinc-900 border-r border-zinc-800 flex flex-col">
        <div className="px-4 py-5 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <span className="text-2xl">♠</span>
            <div>
              <p className="font-bold text-zinc-100 leading-tight">Poker</p>
              <p className="text-xs text-zinc-500">Rush & Cash Analyzer</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-2 py-4 space-y-1">
          {NAV.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                  isActive
                    ? 'bg-green-900/50 text-green-400 font-medium'
                    : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800',
                )
              }
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-4 py-3 border-t border-zinc-800 text-xs text-zinc-600">
          v0.1.0 — lokaal
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-zinc-950">
        <Outlet />
      </main>
    </div>
  )
}
