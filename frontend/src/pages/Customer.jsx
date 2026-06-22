import { useState } from 'react'
import api from '../api/axios'

const BAND_COLOR = { B5: 'bg-purple-600', B4: 'bg-blue-600', B3: 'bg-green-600', B2: 'bg-yellow-500', B1: 'bg-orange-500' }

export default function Customer() {
  const [ghng, setGhng] = useState('')
  const [unit, setUnit] = useState(null)
  const [txnId, setTxnId] = useState('')
  const [loading, setLoading] = useState(false)
  const [payLoading, setPayLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  async function fetchUnit() {
    if (!ghng.trim()) return
    setLoading(true); setError(''); setUnit(null); setResult(null)
    try {
      const { data } = await api.get(`/my-unit/${ghng.trim()}`)
      setUnit(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function pay() {
    if (!txnId.trim()) { setError('Enter Easebuzz Transaction ID'); return }
    setPayLoading(true); setError('')
    try {
      const { data } = await api.post('/pay', {
        ghng: ghng.trim(),
        unit_id: unit.unit_id,
        easebuzz_txn_id: txnId.trim(),
      })
      setResult(data)
      setUnit(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setPayLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold text-white mb-6">Customer Allocation Session</h1>

      {/* GHNG Lookup */}
      <div className="bg-slate-800 rounded-xl p-6 mb-4">
        <label className="block text-sm text-slate-400 mb-1">GHNG Number</label>
        <div className="flex gap-2">
          <input
            className="flex-1 bg-slate-700 text-white rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g. GHNG00123"
            value={ghng}
            onChange={e => setGhng(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && fetchUnit()}
          />
          <button
            onClick={fetchUnit}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg font-medium disabled:opacity-50 transition-colors"
          >
            {loading ? 'Loading…' : 'Fetch Unit'}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-300 rounded-lg px-4 py-3 mb-4 text-sm">
          {error}
        </div>
      )}

      {/* Unit Card */}
      {unit && (
        <div className="bg-slate-800 rounded-xl p-6 mb-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-slate-400 text-xs uppercase tracking-wide mb-1">Your Pre-Allocated Unit</p>
              <p className="text-3xl font-bold text-white">
                Unit {unit.floor}{String(unit.unit_no).padStart(2, '0')}
              </p>
              <p className="text-slate-400 text-sm mt-1">Floor {unit.floor} · Unit {unit.unit_no} · {unit.size_sqft} sq ft</p>
            </div>
            <span className={`${BAND_COLOR[unit.band] || 'bg-slate-600'} text-white text-xs font-bold px-3 py-1 rounded-full`}>
              {unit.band}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-5">
            <div className="bg-slate-700 rounded-lg p-3">
              <p className="text-slate-400 text-xs">Status</p>
              <p className="text-white font-semibold capitalize">{unit.status.replace('_', ' ')}</p>
            </div>
            <div className="bg-slate-700 rounded-lg p-3">
              <p className="text-slate-400 text-xs">Competitors</p>
              <p className="text-white font-semibold">{unit.competing_customers} others</p>
            </div>
          </div>

          {unit.hold_expires_at && (
            <p className="text-yellow-400 text-xs mb-4">
              ⏱ Hold expires: {new Date(unit.hold_expires_at).toLocaleTimeString()}
            </p>
          )}

          <label className="block text-sm text-slate-400 mb-1">Easebuzz Transaction ID</label>
          <div className="flex gap-2">
            <input
              className="flex-1 bg-slate-700 text-white rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-green-500"
              placeholder="EBZ_XXXX"
              value={txnId}
              onChange={e => setTxnId(e.target.value)}
            />
            <button
              onClick={pay}
              disabled={payLoading}
              className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-lg font-medium disabled:opacity-50 transition-colors"
            >
              {payLoading ? 'Processing…' : 'Pay & Secure'}
            </button>
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className={`rounded-xl p-6 ${result.success ? 'bg-green-500/20 border border-green-500' : 'bg-yellow-500/20 border border-yellow-500'}`}>
          {result.success ? (
            <>
              <p className="text-green-400 font-bold text-lg">Unit Secured!</p>
              <p className="text-slate-300 text-sm mt-1">Unit {result.allocated_unit_id} is now yours.</p>
            </>
          ) : (
            <>
              <p className="text-yellow-400 font-bold text-lg">Unit Taken — Moved to Next</p>
              <p className="text-slate-300 text-sm mt-1">
                Next unit: <strong className="text-white">{result.next_unit_id}</strong>
                {result.hold_expires_at && ` · Hold until ${new Date(result.hold_expires_at).toLocaleTimeString()}`}
              </p>
              <button
                onClick={fetchUnit}
                className="mt-3 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm"
              >
                View New Unit
              </button>
            </>
          )}
        </div>
      )}
    </div>
  )
}
