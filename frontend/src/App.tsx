import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './components/Dashboard'
import { HandBrowser } from './components/HandBrowser'
import { HandDetail } from './components/HandDetail'
import { PositionTable } from './components/PositionTable'
import { ImportZone } from './components/ImportZone'
import { HelpPage } from './components/HelpPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="hands" element={<HandBrowser />} />
          <Route path="hands/:id" element={<HandDetail />} />
          <Route path="positions" element={<PositionTable />} />
          <Route path="import" element={<ImportZone />} />
          <Route path="help" element={<HelpPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
