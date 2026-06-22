import { useState, useEffect } from 'react'
import api from '../api/axios'

const PREF_LABEL = { 1: '1st (RERA)', 2: '2nd', 3: '3rd' }
const PREF_COLOR = { 1: 'bg-green-500/20 text-green-400', 2: 'bg-yellow-500/20 text-yellow-400', 3: 'bg-orange-500/20 text-orange-400' }

export default function Admin() {
  const [projectId, setProjectId] = useState(1)
  const [towers, setTowers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Enable preference
  const [prefTarget, setPrefTarget] = useState(2)
  const [prefLoading, setPrefLoading] = useState(false)
  const [prefMsg, setPrefMsg] = useState('')

  // Assign unit
  const [assignGhng, setAssignGhng] = useState('')
  const [assignUnitId, setAssignUnitId] = useState('')
  const [assignLoading, setAssignLoading] = useState(false)
  const [assignMsg, setAssignMsg] = useState('')

  useEffect(() => { fetchDashboard() }, [projectId])

  async function fetchDashboard() {
    setLoading(true); setError('')
    try {
      const { data } = await api.get(`/admin/dashboard/${projectId}`)
      setTowers(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function enablePreference() {
    setPrefLoading(true); setPrefMsg('')
    try {
      const { data } = await api.post('/admin/enable-preference', { project_id: projectId, preference: prefTarget })
      setPrefMsg(`Enabled ${data.enabled} tower(s) for preference ${data.preference}`)
      fetchDashboard()
    } catch (e) {
      setPrefMsg(`Error: ${e.message}`)
    } finally {
      setPrefLoading(false)
    }
  }

  async function assignUnit() {
    if (!assignGhng || !assignUnitId) { setAssignMsg('Fill both fields'); return }
    setAssignLoading(true); setAssignMsg('')
    try {
      await api.post('/admin/assign-unit', { ghng: assignGhng, unit_id: parseInt(assignUnitId) })
      setAssignMsg(`GHNG ${assignGhng} assigned to unit ${assignUnitId}`)
      setAssignGhng(''); setAssignUnitId('')
    } catch (e) {
      setAssignMsg(`Error: ${e.message}`)
    } finally {
      setAssignLoading(false)
    }
  }

  const totalAllocated = towers.reduce((s, t) => s + t.allocated, 0)
  const totalUnits = towers.reduce((s, t) => s + t.total_units, 0)
  const totalAvailable = towers.reduce((s, t) => s + t.available, 0)

  return (
    <div className="max-w-6xl mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold text-white mb-6">Admin Dashboard</h1>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: 'Total Units', value: totalUnits, color: 'text-white' },
          { label: 'Allocated', value: totalAllocated, color: 'text-green-400' },
          { label: 'Available', value: totalAvailable, color: 'text-blue-400' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-slate-800 rounded-xl p-5">
            <p className="text-slate-400 text-sm">{label}</p>
            <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Controls */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        {/* Enable Preference */}
        <div className="bg-slate-800 rounded-xl p-5">
          <p className="text-white font-semibold mb-3">Enable Inventory</p>
          <div className="flex gap-2 mb-3">
            {[2, 3].map(p => (
              <button
                key={p}
                onClick={() => setPrefTarget(p)}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${prefTarget === p ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300'}`}
              >
                {PREF_LABEL[p]} Preference
              </button>
            ))}
          </div>
          <button
            onClick={enablePreference}
            disabled={prefLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50 transition-colors"
          >
            {prefLoading ? 'Enabling…' : `Enable ${PREF_LABEL[prefTarget]} Preference`}
          </button>
          {prefMsg && <p className="text-xs mt-2 text-slate-400">{prefMsg}</p>}
        </div>

        {/* Assign Unit */}
        <div className="bg-slate-800 rounded-xl p-5">
          <p className="text-white font-semibold mb-3">Assign Unit to GHNG</p>
          <input
            className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm mb-2 outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="GHNG Number"
            value={assignGhng}
            onChange={e => setAssignGhng(e.target.value)}
          />
          <input
            className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm mb-3 outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Unit ID (numeric)"
            value={assignUnitId}
            onChange={e => setAssignUnitId(e.target.value)}
          />
          <button
            onClick={assignUnit}
            disabled={assignLoading}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50 transition-colors"
          >
            {assignLoading ? 'Assigning…' : 'Assign Unit'}
          </button>
          {assignMsg && <p className="text-xs mt-2 text-slate-400">{assignMsg}</p>}
        </div>
      </div>

      {/* Refresh */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">Tower Status</h2>
        <button onClick={fetchDashboard} className="text-sm text-blue-400 hover:text-blue-300">
          ↻ Refresh
        </button>
      </div>

      {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

      {/* Tower Grid */}
      {loading ? (
        <p className="text-slate-400 text-sm">Loading…</p>
      ) : (
        <div className="grid grid-cols-3 gap-3">
          {towers.map(t => {
            const fillPct = t.total_units ? Math.round((t.allocated / t.total_units) * 100) : 0
            return (
              <div key={t.tower_id} className={`bg-slate-800 rounded-xl p-4 border ${t.is_active ? 'border-slate-600' : 'border-slate-700 opacity-60'}`}>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="text-white font-semibold">{t.tower_name}</p>
                    <p className="text-slate-400 text-xs">Tower {t.tower_no} · Seq {t.sequence}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${PREF_COLOR[t.preference]}`}>
                      {PREF_LABEL[t.preference]}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${t.is_active ? 'bg-green-500/20 text-green-400' : 'bg-slate-600 text-slate-400'}`}>
                      {t.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>

                {/* Fill bar */}
                <div className="h-1.5 bg-slate-700 rounded-full mb-3">
                  <div
                    className="h-1.5 bg-green-500 rounded-full transition-all"
                    style={{ width: `${fillPct}%` }}
                  />
                </div>

                <div className="grid grid-cols-3 gap-1 text-center">
                  <div>
                    <p className="text-green-400 font-bold text-sm">{t.allocated}</p>
                    <p className="text-slate-500 text-xs">Allocated</p>
                  </div>
                  <div>
                    <p className="text-yellow-400 font-bold text-sm">{t.competing}</p>
                    <p className="text-slate-500 text-xs">Competing</p>
                  </div>
                  <div>
                    <p className="text-blue-400 font-bold text-sm">{t.available}</p>
                    <p className="text-slate-500 text-xs">Available</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
