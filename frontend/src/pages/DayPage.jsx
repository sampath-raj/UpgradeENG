import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { curriculumAPI, progressAPI } from '../api/client'
import { useAuth } from '../context/AuthContext.jsx'
import { useToast } from '../context/ToastContext.jsx'
import {
  BookOpen, Pen, MessageSquare, Trophy, CheckCircle, Circle,
  ChevronLeft, Lightbulb, GraduationCap
} from 'lucide-react'

export default function DayPage() {
  const { dayNumber } = useParams()
  const dayNum = parseInt(dayNumber)
  const { user, refreshUser } = useAuth()
  const { addToast } = useToast()
  const [day, setDay] = useState(null)
  const [dayStatus, setDayStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      curriculumAPI.getDay(dayNum),
      progressAPI.daysStatus(),
    ]).then(([dayRes, statusRes]) => {
      setDay(dayRes.data)
      const status = statusRes.data.find(s => s.day_number === dayNum)
      setDayStatus(status || null)
    }).catch((err) => {
      addToast('Failed to load day content', 'error')
    }).finally(() => setLoading(false))
  }, [dayNum])

  const markModule = async (module) => {
    try {
      const res = await progressAPI.completeModule({ day_number: dayNum, module })
      setDayStatus({ day_number: dayNum, modules_completed: res.data.modules_completed, completed_at: res.data.day_complete ? new Date().toISOString() : null })
      if (res.data.day_complete) {
        addToast('Day completed! 🎉', 'success')
        refreshUser()
      }
    } catch (err) {
      addToast('Failed to update progress', 'error')
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-8 w-48" />
        <div className="skeleton h-40 w-full" />
        <div className="skeleton h-40 w-full" />
      </div>
    )
  }

  if (!day) {
    return <div className="text-center text-surface-200 py-12">Day not found</div>
  }

  const modules = dayStatus?.modules_completed || {}

  const MODULE_LIST = [
    {
      key: 'grammar',
      icon: GraduationCap,
      label: 'Grammar Lesson',
      description: day.grammar_topic,
      action: () => markModule('grammar'),
      inPage: true,
    },
    {
      key: 'vocabulary',
      icon: BookOpen,
      label: 'Vocabulary',
      description: `${day.vocabulary_groups?.length || 0} word groups to practice`,
      link: `/day/${dayNum}/vocab`,
    },
    {
      key: 'writing',
      icon: Pen,
      label: 'Writing',
      description: day.writing_prompt?.substring(0, 80) + '...',
      link: `/day/${dayNum}/writing`,
    },
    {
      key: 'speaking',
      icon: MessageSquare,
      label: 'Speaking Practice',
      description: day.speaking_prompt?.substring(0, 80) + '...',
      link: `/day/${dayNum}/speaking`,
    },
  ]

  if (day.is_milestone_day) {
    MODULE_LIST.push({
      key: 'mock_interview',
      icon: Trophy,
      label: 'Mock Interview',
      description: 'Weekly checkpoint — full mock interview with scoring',
      link: `/day/${dayNum}/interview`,
    })
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* ── Header ─────────────────────────────────────────────── */}
      <div>
        <Link to="/" className="inline-flex items-center gap-1 text-sm text-surface-200 hover:text-primary-400 mb-3 transition-colors">
          <ChevronLeft className="w-4 h-4" /> Back to Dashboard
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="badge badge-info">Day {dayNum}</span>
              <span className="badge badge-neutral">{day.week_theme}</span>
              {day.is_milestone_day && <span className="badge badge-warning">Milestone</span>}
            </div>
            <h1 className="text-2xl font-bold mt-2">{day.focus_topic}</h1>
          </div>
          {dayStatus?.completed_at && (
            <div className="badge badge-success">
              <CheckCircle className="w-3 h-3" /> Completed
            </div>
          )}
        </div>
      </div>

      {/* ── Grammar Lesson (inline) ────────────────────────────── */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-warning-400" />
            Grammar: {day.grammar_topic}
          </h2>
          {modules.grammar ? (
            <span className="badge badge-success"><CheckCircle className="w-3 h-3" /> Done</span>
          ) : (
            <button onClick={() => markModule('grammar')} className="btn-secondary text-xs">
              Mark as Read
            </button>
          )}
        </div>
        <div className="prose prose-invert prose-sm max-w-none text-surface-200 leading-relaxed whitespace-pre-wrap">
          {day.grammar_lesson_md}
        </div>
      </div>

      {/* ── Module Checklist ────────────────────────────────────── */}
      <div className="space-y-3">
        <h2 className="text-lg font-bold">Today's Modules</h2>
        {MODULE_LIST.filter(m => m.key !== 'grammar').map((mod) => {
          const isDone = modules[mod.key]
          const Icon = mod.icon
          const content = (
            <div className={`glass-card p-4 flex items-center gap-4 transition-all ${
              isDone ? 'opacity-60' : 'hover:scale-[1.01]'
            }`}>
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                isDone ? 'bg-success-500/20' : 'bg-primary-500/20'
              }`}>
                <Icon className={`w-5 h-5 ${isDone ? 'text-success-400' : 'text-primary-400'}`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-sm">{mod.label}</h3>
                  {isDone && <CheckCircle className="w-4 h-4 text-success-400" />}
                </div>
                <p className="text-xs text-surface-200 truncate mt-0.5">{mod.description}</p>
              </div>
              {!isDone && (
                <span className="text-xs text-primary-400 font-medium shrink-0">Start →</span>
              )}
            </div>
          )

          return mod.link ? (
            <Link key={mod.key} to={mod.link}>{content}</Link>
          ) : (
            <div key={mod.key}>{content}</div>
          )
        })}
      </div>

      {/* ── Speaking Prompt Preview ─────────────────────────────── */}
      <div className="glass-card-light p-4">
        <h3 className="text-sm font-bold text-surface-200 mb-2">Today's Speaking Prompt</h3>
        <p className="text-sm leading-relaxed">{day.speaking_prompt}</p>
      </div>
    </div>
  )
}
