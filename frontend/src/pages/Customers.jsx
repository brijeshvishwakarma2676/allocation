import { useState, useEffect, useRef } from 'react'
import api from '../api/axios'

const STATUS_COLOR = {
  allocated:     'bg-green-500/20 text-green-400',
  competing:     'bg-yellow-500/20 text-yellow-400',
  hold:          'bg-orange-500/20 text-orange-400',
  pre_allocated: 'bg-blue-500/20 text-blue-400',
}

export default function Customers() {
  const [customers, setCustomers]   = useState([])
  const [total, setTotal]           = useState(0)
  const [page, setPage]             = useState(1)
  const [search, setSearch]         = useState('')
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState('')

  // Single add
  const [addOpen, setAddOpen]       = useState(false)
  const [form, setForm]             = useState({ ghng: '', name: '', phone: '', unit_type_preference: '' })
  const [addLoading, setAddLoading] = useState(false)
  const [addMsg, setAddMsg]         = useState('')

  // Bulk import
  const [bulkOpen, setBulkOpen]     = useState(false)
  const [bulkText, setBulkText]     = useState('')
  const [bulkLoading, setBulkLoading] = useState(false)
  const [bulkMsg, setBulkMsg]       = useState('')
  const fileRef                     = useRef()

  const LIMIT = 50

  useEffect(() => { fetchCustomers() }, [page, search])

  async function fetchCustomers() {
    setLoading(true); setError('')
    try {
      const params = { page, limit: LIMIT }
      if (search.trim()) params.search = search.trim()
      const { data } = await api.get('/customers/', { params })
      setCustomers(data.customers)
      setTotal(data.total)
    } catch (e) {
      setError(e.response?.data?.error || e.message)
    } finally {
      setLoading(false)
    }
  }

  function handleSearch(e) {
    setSearch(e.target.value)
    setPage(1)
  }

  async function addCustomer() {
    if (!form.ghng.trim()) { setAddMsg('GHNG is required'); return }
    setAddLoading(true); setAddMsg('')
    try {
      await api.post('/customers/', form)
      setAddMsg('Customer added successfully')
      setForm({ ghng: '', name: '', phone: '', unit_type_preference: '' })
      fetchCustomers()
    } catch (e) {
      setAddMsg(e.response?.data?.error || e.message)
    } finally {
      setAddLoading(false)
    }
  }

  async function bulkImport() {
    let parsed
    try {
      parsed = JSON.parse(bulkText)
      if (!Array.isArray(parsed)) throw new Error('Must be a JSON array')
    } catch (e) {
      setBulkMsg(`JSON error: ${e.message}`)
      return
    }
    setBulkLoading(true); setBulkMsg('')
    try {
      const { data } = await api.post('/customers/bulk', { customers: parsed })
      setBulkMsg(`Done — ${data.created} created, ${data.skipped} skipped (duplicates)`)
      setBulkText('')
      fetchCustomers()
    } catch (e) {
      setBulkMsg(e.response?.data?.error || e.message)
    } finally {
      setBulkLoading(false)
    }
  }

  function loadFile(e) {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = ev => setBulkText(ev.target.result)
    reader.readAsText(file)
  }

  const totalPages = Math.ceil(total / LIMIT)

  return (
    <div className="max-w-7xl mx-auto py-10 px-4">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Customers</h1>
          <p className="text-slate-400 text-sm mt-0.5">{total} registered</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => { setBulkOpen(!bulkOpen); setAddOpen(false) }}
            className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Bulk Import
          </button>
          <button
            onClick={() => { setAddOpen(!addOpen); setBulkOpen(false) }}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            + Add Customer
          </button>
        </div>
      </div>

      {/* Add Customer Form */}
      {addOpen && (
        <div className="bg-slate-800 rounded-xl p-5 mb-5">
          <h2 className="text-white font-semibold mb-4">Add Customer</h2>
          <div className="grid grid-cols-2 gap-3 mb-3">
            {[
              { key: 'ghng', label: 'GHNG Number *', placeholder: 'GHNG00123' },
              { key: 'name', label: 'Name', placeholder: 'Full name' },
              { key: 'phone', label: 'Phone', placeholder: '+91 9XXXXXXXXX' },
              { key: 'unit_type_preference', label: 'Unit Type', placeholder: '1BHK / 2BHK' },
            ].map(({ key, label, placeholder }) => (
              <div key={key}>
                <label className="text-xs text-slate-400 mb-1 block">{label}</label>
                <input
                  className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder={placeholder}
                  value={form[key]}
                  onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                />
              </div>
            ))}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={addCustomer}
              disabled={addLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm font-medium disabled:opacity-50 transition-colors"
            >
              {addLoading ? 'Saving…' : 'Save Customer'}
            </button>
            {addMsg && (
              <span className={`text-sm ${addMsg.includes('success') ? 'text-green-400' : 'text-red-400'}`}>
                {addMsg}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Bulk Import Form */}
      {bulkOpen && (
        <div className="bg-slate-800 rounded-xl p-5 mb-5">
          <h2 className="text-white font-semibold mb-2">Bulk Import</h2>
          <p className="text-slate-400 text-xs mb-3">
            Paste a JSON array or upload a file. Format:
            <code className="ml-1 text-slate-300">[{"{"}"ghng":"GHNG001","name":"...","phone":"...","unit_type_preference":"1BHK"{"}"},...]</code>
          </p>
          <textarea
            className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-xs font-mono mb-3 outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={8}
            placeholder='[{"ghng":"GHNG001","name":"Amit Shah","phone":"9000000000","unit_type_preference":"2BHK"}]'
            value={bulkText}
            onChange={e => setBulkText(e.target.value)}
          />
          <div className="flex items-center gap-3">
            <button
              onClick={bulkImport}
              disabled={bulkLoading || !bulkText.trim()}
              className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-lg text-sm font-medium disabled:opacity-50 transition-colors"
            >
              {bulkLoading ? 'Importing…' : 'Import'}
            </button>
            <label className="cursor-pointer bg-slate-600 hover:bg-slate-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Upload JSON
              <input ref={fileRef} type="file" accept=".json" className="hidden" onChange={loadFile} />
            </label>
            {bulkMsg && (
              <span className={`text-sm ${bulkMsg.startsWith('Done') ? 'text-green-400' : 'text-red-400'}`}>
                {bulkMsg}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Search */}
      <div className="mb-4">
        <input
          className="w-full max-w-sm bg-slate-800 text-white rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Search by GHNG, name, or phone…"
          value={search}
          onChange={handleSearch}
        />
      </div>

      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-300 rounded-lg px-4 py-3 text-sm mb-4">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700">
              {['GHNG', 'Name', 'Phone', 'Unit Pref', 'Status', 'Registered'].map(h => (
                <th key={h} className="text-left text-slate-400 font-medium px-4 py-3 text-xs uppercase tracking-wide">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="text-center text-slate-400 py-10">Loading…</td>
              </tr>
            ) : customers.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center text-slate-500 py-10">No customers found</td>
              </tr>
            ) : (
              customers.map((c, i) => (
                <tr
                  key={c.ghng}
                  className={`border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors ${i % 2 === 0 ? '' : 'bg-slate-800/50'}`}
                >
                  <td className="px-4 py-3 font-mono text-white font-medium">{c.ghng}</td>
                  <td className="px-4 py-3 text-slate-200">{c.name || <span className="text-slate-500">—</span>}</td>
                  <td className="px-4 py-3 text-slate-300">{c.phone || <span className="text-slate-500">—</span>}</td>
                  <td className="px-4 py-3 text-slate-300">{c.unit_type_preference || <span className="text-slate-500">—</span>}</td>
                  <td className="px-4 py-3">
                    {c.allocation_status ? (
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLOR[c.allocation_status] || 'bg-slate-600 text-slate-300'}`}>
                        {c.allocation_status.replace('_', ' ')}
                      </span>
                    ) : (
                      <span className="text-slate-500 text-xs">unassigned</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-slate-400 text-xs">
                    {c.registered_at ? new Date(c.registered_at).toLocaleDateString() : '—'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <span className="text-slate-400 text-sm">
            Page {page} of {totalPages} · {total} total
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="bg-slate-700 hover:bg-slate-600 text-white px-3 py-1.5 rounded-lg text-sm disabled:opacity-40 transition-colors"
            >
              ← Prev
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="bg-slate-700 hover:bg-slate-600 text-white px-3 py-1.5 rounded-lg text-sm disabled:opacity-40 transition-colors"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
