import { useState } from 'react'
import api from '../api/axios'

const STAGES = ['mands_review', 'finance_review', 'preaudit_review', 'banking', 'complete']
const STAGE_LABEL = {
  mands_review:    'M&SS Review',
  finance_review:  'Finance Review',
  preaudit_review: 'Pre-Audit Review',
  banking:         'Banking',
  complete:        'Complete',
  rejected:        'Rejected',
}

export default function Cancellation() {
  // Request cancellation
  const [ghng, setGhng] = useState('')
  const [unitId, setUnitId] = useState('')
  const [reason, setReason] = useState('')
  const [reqLoading, setReqLoading] = useState(false)
  const [reqResult, setReqResult] = useState(null)

  // Check status
  const [cancelId, setCancelId] = useState('')
  const [status, setStatus] = useState(null)
  const [statusLoading, setStatusLoading] = useState(false)

  // Review
  const [reviewId, setReviewId] = useState('')
  const [reviewAction, setReviewAction] = useState('approved')
  const [reviewRole, setReviewRole] = useState('mands')
  const [reviewReason, setReviewReason] = useState('')
  const [refundRef, setRefundRef] = useState('')
  const [reviewLoading, setReviewLoading] = useState(false)
  const [reviewMsg, setReviewMsg] = useState('')

  const [error, setError] = useState('')

  async function requestCancel() {
    if (!ghng || !unitId || !reason) { setError('Fill all fields'); return }
    setReqLoading(true); setError('')
    try {
      const { data } = await api.post('/request', { ghng, unit_id: parseInt(unitId), reason })
      setReqResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setReqLoading(false)
    }
  }

  async function checkStatus() {
    if (!cancelId) return
    setStatusLoading(true); setError('')
    try {
      const { data } = await api.get(`/status/${cancelId}`)
      setStatus(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setStatusLoading(false)
    }
  }

  async function submitReview() {
    if (!reviewId) { setReviewMsg('Enter Cancellation ID'); return }
    setReviewLoading(true); setReviewMsg('')
    try {
      const payload = {
        cancellation_id: parseInt(reviewId),
        action: reviewAction,
        actor_role: reviewRole,
        reason: reviewReason || null,
        refund_reference_id: refundRef || null,
      }
      const { data } = await api.post('/review', payload)
      setReviewMsg(`Done — new stage: ${STAGE_LABEL[data.stage] || data.stage}`)
    } catch (e) {
      setReviewMsg(`Error: ${e.message}`)
    } finally {
      setReviewLoading(false)
    }
  }

  const stageIdx = status ? STAGES.indexOf(status.stage) : -1

  return (
    <div className="max-w-3xl mx-auto py-10 px-4 space-y-6">
      <h1 className="text-2xl font-bold text-white">Cancellation & Refund</h1>

      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-300 rounded-lg px-4 py-3 text-sm">{error}</div>
      )}

      {/* Request Cancellation */}
      <div className="bg-slate-800 rounded-xl p-6">
        <h2 className="text-white font-semibold mb-4">Request Cancellation</h2>
        <div className="grid grid-cols-2 gap-3 mb-3">
          <div>
            <label className="text-xs text-slate-400 mb-1 block">GHNG Number</label>
            <input className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="GHNG00123" value={ghng} onChange={e => setGhng(e.target.value)} />
          </div>
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Unit ID</label>
            <input className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="123" value={unitId} onChange={e => setUnitId(e.target.value)} />
          </div>
        </div>
        <textarea className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm mb-3 outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          rows={3} placeholder="Reason for cancellation" value={reason} onChange={e => setReason(e.target.value)} />
        <button onClick={requestCancel} disabled={reqLoading}
          className="bg-red-600 hover:bg-red-700 text-white px-5 py-2 rounded-lg text-sm font-medium disabled:opacity-50 transition-colors">
          {reqLoading ? 'Submitting…' : 'Submit Cancellation'}
        </button>
        {reqResult && (
          <p className="text-green-400 text-sm mt-3">
            Submitted! Cancellation ID: <strong>{reqResult.cancellation_id}</strong> · Stage: {STAGE_LABEL[reqResult.stage]}
          </p>
        )}
      </div>

      {/* Check Status */}
      <div className="bg-slate-800 rounded-xl p-6">
        <h2 className="text-white font-semibold mb-4">Track Status</h2>
        <div className="flex gap-2 mb-4">
          <input className="flex-1 bg-slate-700 text-white rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Cancellation ID" value={cancelId} onChange={e => setCancelId(e.target.value)} />
          <button onClick={checkStatus} disabled={statusLoading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50 transition-colors">
            {statusLoading ? '…' : 'Check'}
          </button>
        </div>

        {status && (
          <>
            <div className="flex items-center gap-2 mb-4">
              {STAGES.map((s, i) => (
                <div key={s} className="flex items-center gap-2">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold
                    ${status.stage === 'rejected' && i <= stageIdx ? 'bg-red-500 text-white' :
                      i < stageIdx ? 'bg-green-500 text-white' :
                      i === stageIdx ? 'bg-blue-500 text-white' : 'bg-slate-600 text-slate-400'}`}>
                    {i < stageIdx ? '✓' : i + 1}
                  </div>
                  <span className="text-xs text-slate-400 hidden sm:block">{STAGE_LABEL[s]}</span>
                  {i < STAGES.length - 1 && <div className={`h-px w-4 ${i < stageIdx ? 'bg-green-500' : 'bg-slate-600'}`} />}
                </div>
              ))}
            </div>

            {status.stage === 'rejected' && (
              <p className="text-red-400 text-sm mb-3">Cancellation was rejected.</p>
            )}

            {status.logs?.length > 0 && (
              <div className="space-y-2">
                {status.logs.map((log, i) => (
                  <div key={i} className="flex items-center gap-3 bg-slate-700 rounded-lg px-3 py-2 text-xs">
                    <span className={`font-bold ${log.action === 'approved' ? 'text-green-400' : 'text-red-400'}`}>
                      {log.action.toUpperCase()}
                    </span>
                    <span className="text-slate-400">{STAGE_LABEL[log.stage]}</span>
                    <span className="text-slate-500">by {log.actor_role}</span>
                    {log.reason && <span className="text-slate-400">— {log.reason}</span>}
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Internal Review Panel */}
      <div className="bg-slate-800 rounded-xl p-6">
        <h2 className="text-white font-semibold mb-4">Internal Review Panel</h2>
        <div className="grid grid-cols-2 gap-3 mb-3">
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Cancellation ID</label>
            <input className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. 1" value={reviewId} onChange={e => setReviewId(e.target.value)} />
          </div>
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Your Role</label>
            <select className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
              value={reviewRole} onChange={e => setReviewRole(e.target.value)}>
              <option value="mands">M&SS</option>
              <option value="finance">Finance</option>
              <option value="preaudit">Pre-Audit</option>
              <option value="banking">Banking</option>
            </select>
          </div>
        </div>
        <div className="flex gap-2 mb-3">
          {['approved', 'rejected'].map(a => (
            <button key={a} onClick={() => setReviewAction(a)}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors
                ${reviewAction === a
                  ? a === 'approved' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                  : 'bg-slate-700 text-slate-300'}`}>
              {a.charAt(0).toUpperCase() + a.slice(1)}
            </button>
          ))}
        </div>
        <input className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm mb-2 outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Reason (optional / required on reject)" value={reviewReason} onChange={e => setReviewReason(e.target.value)} />
        {reviewRole === 'banking' && reviewAction === 'approved' && (
          <input className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm mb-2 outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Refund Reference ID" value={refundRef} onChange={e => setRefundRef(e.target.value)} />
        )}
        <button onClick={submitReview} disabled={reviewLoading}
          className="bg-slate-600 hover:bg-slate-500 text-white px-5 py-2 rounded-lg text-sm font-medium disabled:opacity-50 transition-colors">
          {reviewLoading ? 'Submitting…' : 'Submit Review'}
        </button>
        {reviewMsg && <p className="text-sm mt-2 text-slate-400">{reviewMsg}</p>}
      </div>
    </div>
  )
}
