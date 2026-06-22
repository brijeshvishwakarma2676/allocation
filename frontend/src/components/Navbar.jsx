import { NavLink } from 'react-router-dom'

export default function Navbar() {
  const link = 'px-4 py-2 rounded-lg text-sm font-medium transition-colors'
  const active = 'bg-blue-600 text-white'
  const inactive = 'text-slate-300 hover:bg-slate-700'

  return (
    <nav className="bg-slate-900 border-b border-slate-700 px-6 py-3 flex items-center gap-6">
      <span className="text-white font-bold text-lg tracking-tight">
        Naigaon <span className="text-blue-400">Allocation</span>
      </span>
      <div className="flex gap-2 ml-6">
        <NavLink to="/" end className={({ isActive }) => `${link} ${isActive ? active : inactive}`}>
          Customer
        </NavLink>
        <NavLink to="/admin" className={({ isActive }) => `${link} ${isActive ? active : inactive}`}>
          Admin Dashboard
        </NavLink>
        <NavLink to="/cancellation" className={({ isActive }) => `${link} ${isActive ? active : inactive}`}>
          Cancellation
        </NavLink>
        <NavLink to="/customers" className={({ isActive }) => `${link} ${isActive ? active : inactive}`}>
          Customers
        </NavLink>
      </div>
    </nav>
  )
}
