import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Customer from './pages/Customer'
import Admin from './pages/Admin'
import Cancellation from './pages/Cancellation'
import Customers from './pages/Customers'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-900">
        <Navbar />
        <Routes>
          <Route path="/" element={<Customer />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/cancellation" element={<Cancellation />} />
          <Route path="/customers" element={<Customers />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
