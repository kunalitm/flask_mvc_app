import axios from 'axios'

const API_BASE_URL = '/api'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth Service
export const authService = {
  login: async (username, password) => {
    const response = await api.post('/users/login', { username, password })
    if (response.data.token) {
      localStorage.setItem('token', response.data.token)
    }
    return response.data
  },
  logout: () => {
    localStorage.removeItem('token')
  },
  getToken: () => {
    return localStorage.getItem('token')
  },
  getCurrentUser: async () => {
    const response = await api.get('/users/me')
    return response.data
  },
}

// User Service
export const userService = {
  getAll: async (page = 1, perPage = 10) => {
    const response = await api.get(`/users/?page=${page}&per_page=${perPage}`)
    return response.data
  },
  getById: async (id) => {
    const response = await api.get(`/users/${id}`)
    return response.data
  },
  create: async (userData) => {
    const response = await api.post('/users/', userData)
    return response.data
  },
  update: async (id, userData) => {
    const response = await api.put(`/users/${id}`, userData)
    return response.data
  },
  delete: async (id) => {
    const response = await api.delete(`/users/${id}`)
    return response.data
  },
  assignRole: async (userId, roleId) => {
    const response = await api.post(`/users/${userId}/roles`, { role_id: roleId })
    return response.data
  },
  removeRole: async (userId, roleId) => {
    const response = await api.delete(`/users/${userId}/roles/${roleId}`)
    return response.data
  },
}

// Role Service
export const roleService = {
  getAll: async () => {
    const response = await api.get('/roles/')
    return response.data
  },
  getById: async (id) => {
    const response = await api.get(`/roles/${id}`)
    return response.data
  },
  create: async (roleData) => {
    const response = await api.post('/roles/', roleData)
    return response.data
  },
  update: async (id, roleData) => {
    const response = await api.put(`/roles/${id}`, roleData)
    return response.data
  },
  delete: async (id) => {
    const response = await api.delete(`/roles/${id}`)
    return response.data
  },
  getPermissions: async (id) => {
    const response = await api.get(`/roles/${id}/permissions`)
    return response.data
  },
  updatePermissions: async (id, permissions) => {
    const response = await api.put(`/roles/${id}/permissions`, { permissions })
    return response.data
  },
}

// Plugin Service
export const pluginService = {
  getAll: async () => {
    const response = await api.get('/plugins/')
    return response.data
  },
  getById: async (id) => {
    const response = await api.get(`/plugins/${id}`)
    return response.data
  },
  enable: async (id) => {
    const response = await api.post(`/plugins/${id}/enable`)
    return response.data
  },
  disable: async (id) => {
    const response = await api.post(`/plugins/${id}/disable`)
    return response.data
  },
  getConfig: async (id) => {
    const response = await api.get(`/plugins/${id}/config`)
    return response.data
  },
  updateConfig: async (id, config) => {
    const response = await api.put(`/plugins/${id}/config`, { config })
    return response.data
  },
  reload: async (id) => {
    const response = await api.post(`/plugins/${id}/reload`)
    return response.data
  },
  discover: async () => {
    const response = await api.post('/plugins/discover')
    return response.data
  },
  getEnabled: async () => {
    const response = await api.get('/plugins/enabled')
    return response.data
  },
}

// Stock Service
export const stockService = {
  getAll: async () => {
    const response = await api.get('/stock/items')
    return response.data
  },
  getById: async (id) => {
    const response = await api.get(`/stock/items/${id}`)
    return response.data
  },
  create: async (itemData) => {
    const response = await api.post('/stock/items', itemData)
    return response.data
  },
  update: async (id, itemData) => {
    const response = await api.put(`/stock/items/${id}`, itemData)
    return response.data
  },
  delete: async (id) => {
    const response = await api.delete(`/stock/items/${id}`)
    return response.data
  },
  getStats: async () => {
    const response = await api.get('/stock/stats')
    return response.data
  },
}

export default api
