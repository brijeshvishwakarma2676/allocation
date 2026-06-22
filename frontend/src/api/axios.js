import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/allocation',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  res => res,
  err => {
    const msg = err.response?.data?.error || err.message || 'Something went wrong'
    return Promise.reject(new Error(msg))
  }
)

export default api
