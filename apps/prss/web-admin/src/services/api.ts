import axios from 'axios'

const api = axios.create({
  baseURL: '/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const returnsApi = {
  list: (params?: any) => api.get('/returns', { params }),
  get: (id: number) => api.get(`/returns/${id}`),
  create: (data: any) => api.post('/returns', data),
  receive: (id: number, data: any) => api.post(`/returns/${id}/receive`, data),
  inspect: (id: number, data: any) => api.post(`/returns/${id}/inspect`, data),
  decide: (id: number, data: any) => api.post(`/returns/${id}/decide`, data),
}

export const reportsApi = {
  getKPIs: () => api.get('/reports/kpis'),
  getTopReasons: () => api.get('/reports/top-reasons'),
}

export const authApi = {
  login: (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return api.post('/auth/token', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export default api
