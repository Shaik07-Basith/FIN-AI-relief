const API_BASE = '/api'

function getToken() {
  return localStorage.getItem('finrelief_token')
}

export function setToken(token) {
  if (token) localStorage.setItem('finrelief_token', token)
  else localStorage.removeItem('finrelief_token')
}

async function request(path, { method = 'GET', body, form } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  let payload = undefined
  if (form) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    payload = new URLSearchParams(form).toString()
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
    payload = JSON.stringify(body)
  }

  const res = await fetch(`${API_BASE}${path}`, { method, headers, body: payload })

  if (res.status === 204) return null

  let data = null
  try {
    data = await res.json()
  } catch {
    // no JSON body
  }

  if (!res.ok) {
    const message = data?.detail || `Request failed (${res.status})`
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message))
  }

  return data
}

export const api = {
  register: (payload) => request('/auth/register', { method: 'POST', body: payload }),
  login: (email, password) =>
    request('/auth/login', { method: 'POST', form: { username: email, password } }),
  me: () => request('/auth/me'),

  getLoans: () => request('/loans'),
  createLoan: (payload) => request('/loans', { method: 'POST', body: payload }),
  updateLoan: (id, payload) => request(`/loans/${id}`, { method: 'PUT', body: payload }),
  deleteLoan: (id) => request(`/loans/${id}`, { method: 'DELETE' }),
  getLoanSettlements: (id) => request(`/loans/${id}/settlements`),

  getFinancialProfile: () => request('/financial-profile'),
  updateFinancialProfile: (payload) => request('/financial-profile', { method: 'PUT', body: payload }),
  getDashboard: () => request('/financial-profile/dashboard'),

  getSettlements: (priority) => request(`/settlements${priority ? `?priority=${priority}` : ''}`),

  generateNegotiation: (loan_id, tone) =>
    request('/ai/negotiate', { method: 'POST', body: { loan_id, tone } }),
  getNegotiations: () => request('/ai/negotiations'),
  getAiHistory: () => request('/ai/history'),
}
