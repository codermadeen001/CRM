import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

export const authService = {
  async login(username, password) {
    const response = await api.post('/auth/login/', { username, password })
    return response.data
  },

  async logout() {
    await api.post('/auth/logout/')
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },
}

export const crmService = {
  // Dashboard
  async getDashboardStats() {
    const response = await api.get('/dashboard/stats/')
    return response.data
  },

  // Companies
  async getCompanies() {
    const response = await api.get('/companies/')
    return response.data
  },
  async getCompany(id) {
    const response = await api.get(`/companies/${id}/`)
    return response.data
  },
  async createCompany(data) {
    const response = await api.post('/companies/', data)
    return response.data
  },
  async updateCompany(id, data) {
    const response = await api.put(`/companies/${id}/`, data)
    return response.data
  },
  async deleteCompany(id) {
    await api.delete(`/companies/${id}/`)
  },

  // Contacts
  async getContacts() {
    const response = await api.get('/contacts/')
    return response.data
  },
  async getContact(id) {
    const response = await api.get(`/contacts/${id}/`)
    return response.data
  },
  async createContact(data) {
    const response = await api.post('/contacts/', data)
    return response.data
  },
  async updateContact(id, data) {
    const response = await api.put(`/contacts/${id}/`, data)
    return response.data
  },
  async deleteContact(id) {
    await api.delete(`/contacts/${id}/`)
  },

  // Deals
  async getDeals() {
    const response = await api.get('/deals/')
    return response.data
  },
  async getDeal(id) {
    const response = await api.get(`/deals/${id}/`)
    return response.data
  },
  async createDeal(data) {
    const response = await api.post('/deals/', data)
    return response.data
  },
  async updateDeal(id, data) {
    const response = await api.put(`/deals/${id}/`, data)
    return response.data
  },
  async deleteDeal(id) {
    await api.delete(`/deals/${id}/`)
  },

  // Tasks
  async getTasks() {
    const response = await api.get('/tasks/')
    return response.data
  },
  async getTask(id) {
    const response = await api.get(`/tasks/${id}/`)
    return response.data
  },
  async createTask(data) {
    const response = await api.post('/tasks/', data)
    return response.data
  },
  async updateTask(id, data) {
    const response = await api.put(`/tasks/${id}/`, data)
    return response.data
  },
  async deleteTask(id) {
    await api.delete(`/tasks/${id}/`)
  },


  //meetings
  
async getMeetings() {
    const response = await api.get('/meetings/')
    return response.data
},
async getMeeting(id) {
    const response = await api.get(`/meetings/${id}/`)
    return response.data
},
async createMeeting(data) {
    const response = await api.post('/meetings/create/', data)
    return response.data
},
async updateMeeting(id, data) {
    const response = await api.put(`/meetings/update/${id}/`, data)
    return response.data
},
async deleteMeeting(id) {
    const response = await api.delete(`/meetings/delete/${id}/`)
    return response.data
},
async getTodaysMeetingCount() {
    const response = await api.get('/meetings/today/count/')
    return response.data
},

async getMeetingsForDeal(dealId) {
    const response = await api.get(`/meetings/filter/?deal=${dealId}`)
    return response.data
},
async getMeetingsForCompany(companyId) {
    const response = await api.get(`/meetings/filter/?company=${companyId}`)
    return response.data
},

}

export default api
