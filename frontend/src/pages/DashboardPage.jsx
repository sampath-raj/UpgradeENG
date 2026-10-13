import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { curriculumAPI, progressAPI } from '../api/client'
import {
  Flame, CheckCircle, BookOpen, Pen, MessageSquare, Trophy, Lock, Star, ChevronRight
} from 'lucide-react'

const WEEK_COLORS = {
  'Foundation': 'from-blue-500/20 to-blue-600/10 border-blue-500/30',
  'Thinking in English': 'from-purple-500/20 to-purple-600/10 border-purple-500/30',
  'Interview English': 'from-emerald-500/20 to-emerald-600/10 border-emerald-500/30',
  'Pressure Training': 'from-orange-500/20 to-orange-600/10 border-orange-500/30',
}

export default function DashboardPage() {
  const { user } = useAuth()
  const [days, setDays] = useState([])
  const [progress, setProgress] = useState(null)
  const [daysStatus, setDaysStatus] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      curriculumAPI.listDays(),
      progressAPI.summary(),
      progressAPI.daysStatus(),
    ]).then(([daysRes, progRes, statusRes]) => {
      setDays(daysRes.data)
      setProgress(progRes.data)
      setDaysStatus(statusRes.data)
    }).catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const currentDay = user?.current_day || 0
  const statusMap = {}
  daysStatus.forEach(s => { statusMap[s.day_number] = s })

  if (loading) {
    return (
      <div className="space-y-4">
        {[1,2,3].map(i => <div key={i} className="skeleton h-24 w-full" />)}
      </div>
    )
  }

  // Group days by week
  const weeks = {}
  days.forEach(d => {
    if (!weeks[d.week_number]) weeks[d.week_number] = { theme: d.week_theme, days: [] }
    weeks[d.week_number].days.push(d)
  })

  return (
    <div className="space-y-8">
      {/* ── Welcome + Stats ──────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">
            Welcome back, <span className="gradient-text">{user?.name}</span>
          </h1>
          <p className="text-surface-200 mt-1">
            {currentDay === 0
              ? 'Start your journey — complete the baseline interview!'
              : currentDay >= 30
                ? 'Congratulations! You\'ve completed the 30-day program! 🎉'
                : `Day ${currentDay + 1} is ready for you`}
          </p>
        </div>
      </div>

      {/* ── Stat cards ───────────────────────────────────────────── */}
      {progress && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="glass-card p-4 text-center">
            <Flame className="w-6 h-6 text-orange-400 mx-auto mb-1" />
            <div className="text-2xl font-bold">{progress.streak_count}</div>
            <div className="text-xs text-surface-200">Day Streak</div>
          </div>
          <div className="glass-card p-4 text-center">
            <CheckCircle className="w-6 h-6 text-success-400 mx-auto mb-1" />
            <div className="text-2xl font-bold">{progress.days_completed}/30</div>
            <div className="text-xs text-surface-200">Days Done</div>
          </div>
          <div className="glass-card p-4 text-center">
            <BookOpen className="w-6 h-6 text-primary-400 mx-auto mb-1" />
            <div className="text-2xl font-bold">{progress.vocab_groups_mastered}</div>
            <div className="text-xs text-surface-200">Vocab Mastered</div>
          </div>
          <div className="glass-card p-4 text-center">
            <Trophy className="w-6 h-6 text-accent-400 mx-auto mb-1" />
            <div className="text-2xl font-bold">{progress.mock_interviews_completed}</div>
            <div className="text-xs text-surface-200">Interviews</div>
          </div>
        </div>
      )}

      {/* ── Overall progress bar ─────────────────────────────────── */}
      <div className="glass-card p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Overall Progress</span>
          <span className="text-sm text-surface-200">{progress?.days_completed || 0}/30 days</span>
        </div>
        <div className="progress-bar-bg">
          <div
            className="progress-bar-fill"
            style={{ width: `${((progress?.days_completed || 0) / 30) * 100}%` }}
          />
        </div>
      </div>

      {/* ── Baseline interview CTA ───────────────────────────────── */}
      {currentDay === 0 && (
        <Link to="/day/0/interview" className="block">
          <div className="glass-card p-6 border-2 border-primary-500/30 hover:border-primary-500/50 transition-all">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-primary-500/20 flex items-center justify-center shrink-0">
                <Star className="w-6 h-6 text-primary-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-lg">Start Your Journey</h3>
                <p className="text-surface-200 text-sm">Take the baseline interview to measure your starting point</p>
              </div>
              <ChevronRight className="w-5 h-5 text-surface-200" />
            </div>
          </div>
        </Link>
      )}

      {/* ── Week groups ──────────────────────────────────────────── */}
      {Object.entries(weeks).map(([weekNum, { theme, days: weekDays }]) => (
        <div key={weekNum} className="space-y-3">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <span className="text-surface-200">Week {weekNum}:</span> {theme}
          </h2>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {weekDays.map((day) => {
              const status = statusMap[day.day_number]
              const isCompleted = status?.completed_at
              const isUnlocked = day.day_number <= currentDay + 1
              const isCurrent = day.day_number === currentDay + 1

              return (
                <Link
                  key={day.day_number}
                  to={isUnlocked ? `/day/${day.day_number}` : '#'}
                  className={`glass-card p-4 transition-all ${
                    !isUnlocked ? 'opacity-40 cursor-not-allowed' : 'hover:scale-[1.02]'
                  } ${isCurrent ? 'ring-2 ring-primary-500/50' : ''}`}
                  onClick={(e) => !isUnlocked && e.preventDefault()}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-bold text-surface-200">
                          DAY {day.day_number}
                        </span>
                        {day.is_milestone_day && (
                          <span className="badge badge-warning text-[10px]">
                            <Trophy className="w-3 h-3" /> Milestone
                          </span>
                        )}
                      </div>
                      <h3 className="font-semibold text-sm truncate">{day.focus_topic}</h3>
                      <p className="text-xs text-surface-200 mt-1 truncate">{day.grammar_topic}</p>
                    </div>
                    <div className="ml-2 shrink-0">
                      {isCompleted ? (
                        <CheckCircle className="w-5 h-5 text-success-400" />
                      ) : !isUnlocked ? (
                        <Lock className="w-5 h-5 text-surface-700" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-surface-200" />
                      )}
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}
