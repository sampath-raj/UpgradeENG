import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
})

// ── Token helpers ─────────────────────────────────────────────────────────────
const TOKEN_KEY = 'token'
const TOKEN_ISSUED_KEY = 'token_issued_at'
// Refresh when less than 1 day remains on the 7-day token
const REFRESH_THRESHOLD_MS = 24 * 60 * 60 * 1000  // 1 day in ms
const TOKEN_TTL_MS = 7 * 24 * 60 * 60 * 1000       // 7 days in ms

export function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(TOKEN_ISSUED_KEY, String(Date.now()))
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(TOKEN_ISSUED_KEY)
}

function isTokenNearExpiry() {
  const issuedAt = parseInt(localStorage.getItem(TOKEN_ISSUED_KEY) || '0', 10)
  if (!issuedAt) return false
  const age = Date.now() - issuedAt
  return age > TOKEN_TTL_MS - REFRESH_THRESHOLD_MS
}

// ── Attach JWT to every request + auto-refresh ────────────────────────────────
let _refreshing = false

api.interceptors.request.use(async (config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`

    // Auto-refresh if token is near expiry and we're not already refreshing
    if (isTokenNearExpiry() && !_refreshing && !config.url?.includes('/auth/refresh')) {
      _refreshing = true
      try {
        const res = await axios.post(
          `${API_BASE}/api/auth/refresh`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        )
        saveToken(res.data.access_token)
        config.headers.Authorization = `Bearer ${res.data.access_token}`
      } catch {
        // Refresh failed — let the request proceed; the 401 handler will log out
      } finally {
        _refreshing = false
      }
    }
  }
  return config
})

// ── Handle 401 globally ───────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearToken()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
  refresh: () => api.post('/auth/refresh'),
}

// ── Curriculum ───────────────────────────────────────────────────────────────
export const curriculumAPI = {
  listDays: () => api.get('/curriculum/days'),
  getDay: (dayNumber) => api.get(`/curriculum/days/${dayNumber}`),
}

// ── Writing ──────────────────────────────────────────────────────────────────
export const writingAPI = {
  submit: (data) => api.post('/writing/submit', data),
  history: (dayNumber) => api.get('/writing/history', { params: { day_number: dayNumber } }),
  getSubmission: (id) => api.get(`/writing/${id}`),
}

// ── Vocabulary ───────────────────────────────────────────────────────────────
export const vocabAPI = {
  getForDay: (dayNumber) => api.get(`/vocab/day/${dayNumber}`),
  getReview: () => api.get('/vocab/review'),
  practice: (data) => api.post('/vocab/practice', data),
  checkMastered: (data) => api.post('/vocab/check-mastered', data),
  status: () => api.get('/vocab/status'),
}

// ── Speaking ─────────────────────────────────────────────────────────────────
export const speakingAPI = {
  chat: (data) => api.post('/speaking/chat', data),
  end: (data) => api.post('/speaking/end', data),
}

// ── Mock Interview ───────────────────────────────────────────────────────────
export const interviewAPI = {
  start: (data) => api.post('/mock-interview/start', data),
  respond: (data) => api.post('/mock-interview/respond', data),
  finish: (data) => api.post('/mock-interview/finish', data),
  list: () => api.get('/mock-interview/list'),
}

// ── Progress ─────────────────────────────────────────────────────────────────
export const progressAPI = {
  summary: () => api.get('/progress/summary'),
  trend: () => api.get('/progress/trend'),
  comparison: () => api.get('/progress/comparison'),
  completeModule: (data) => api.post('/progress/day-complete', data),
  daysStatus: () => api.get('/progress/days-status'),
}

export default api
