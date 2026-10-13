import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext.jsx'
import Layout from './components/Layout.jsx'
import LoginPage from './pages/LoginPage.jsx'
import SignupPage from './pages/SignupPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import DayPage from './pages/DayPage.jsx'
import WritingPage from './pages/WritingPage.jsx'
import VocabPage from './pages/VocabPage.jsx'
import SpeakingPage from './pages/SpeakingPage.jsx'
import MockInterviewPage from './pages/MockInterviewPage.jsx'
import ProgressPage from './pages/ProgressPage.jsx'
import ComparisonPage from './pages/ComparisonPage.jsx'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="skeleton w-12 h-12 rounded-full" />
      </div>
    )
  }
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<DashboardPage />} />
        <Route path="day/:dayNumber" element={<DayPage />} />
        <Route path="day/:dayNumber/writing" element={<WritingPage />} />
        <Route path="day/:dayNumber/vocab" element={<VocabPage />} />
        <Route path="day/:dayNumber/speaking" element={<SpeakingPage />} />
        <Route path="day/:dayNumber/interview" element={<MockInterviewPage />} />
        <Route path="progress" element={<ProgressPage />} />
        <Route path="comparison" element={<ComparisonPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
