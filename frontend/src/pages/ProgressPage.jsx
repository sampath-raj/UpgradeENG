import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { progressAPI, vocabAPI, interviewAPI } from '../api/client'
import { useAuth } from '../context/AuthContext.jsx'
import {
  TrendingUp, Flame, CheckCircle, BookOpen, Trophy, Pen, BarChart3
} from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'

const SCORE_COLORS = {
  grammar: '#3b82f6',
  vocabulary: '#8b5cf6',
  fluency: '#22c55e',
  structure: '#f59e0b',
  overall: '#ef4444',
}

export default function ProgressPage() {
  const { user } = useAuth()
  const [summary, setSummary] = useState(null)
  const [trend, setTrend] = useState([])
  const [vocabStatus, setVocabStatus] = useState(null)
  const [interviews, setInterviews] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      progressAPI.summary(),
      progressAPI.trend(),
      vocabAPI.status(),
      interviewAPI.list(),
    ]).then(([sumRes, trendRes, vocRes, intRes]) => {
      setSummary(sumRes.data)
      setTrend(trendRes.data)
      setVocabStatus(vocRes.data)
      setInterviews(intRes.data)
    }).catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="space-y-4">
        {[1,2,3].map(i => <div key={i} className="skeleton h-32 w-full" />)}
      </div>
    )
  }

  // Prepare chart data
  const chartData = trend.map(t => ({
    name: `Day ${t.day_number}`,
    grammar: t.scores.grammar,
    vocabulary: t.scores.vocabulary,
    fluency: t.scores.fluency,
    structure: t.scores.structure,
    overall: t.scores.overall,
  }))

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <TrendingUp className="w-6 h-6 text-primary-400" />
        Your Progress
      </h1>

      {/* ── Stat cards ───────────────────────────────────────── */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="glass-card p-4 text-center">
            <Flame className="w-6 h-6 text-orange-400 mx-auto mb-1" />
            <div className="text-2xl font-bold">{summary.streak_count}</div>
            <div className="text-xs text-surface-200">Day Streak</div>
          </div>
          <div className="glass-card p-4 text-center">
            <CheckCircle className="w-6 h-6 text-success-400 mx-auto mb-1" />
            <div className="text-2xl font-bold">{summary.days_completed}/30</div>
            <div className="text-xs text-surface-200">Days Done</div>
          </div>
          <div className="glass-card p-4 text-center">
            <BookOpen className="w-6 h-6 text-primary-400 mx-auto mb-1" />
            <div className="text-2xl font-bold">
              {summary.vocab_groups_mastered}/{summary.vocab_groups_total}
            </div>
            <div className="text-xs text-surface-200">Vocab Mastered</div>
          </div>
          <div className="glass-card p-4 text-center">
            <Pen className="w-6 h-6 text-accent-400 mx-auto mb-1" />
            <div className="text-2xl font-bold">{summary.writing_submissions}</div>
            <div className="text-xs text-surface-200">Writing Submissions</div>
          </div>
        </div>
      )}

      {/* ── Progress bar ─────────────────────────────────────── */}
      <div className="glass-card p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Program Progress</span>
          <span className="text-sm text-surface-200">{summary?.days_completed || 0}/30</span>
        </div>
        <div className="progress-bar-bg">
          <div
            className="progress-bar-fill"
            style={{ width: `${((summary?.days_completed || 0) / 30) * 100}%` }}
          />
        </div>
      </div>

      {/* ── Vocabulary stats ─────────────────────────────────── */}
      {vocabStatus && (
        <div className="glass-card p-5">
          <h2 className="font-bold text-lg mb-3 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-primary-400" /> Vocabulary Progress
          </h2>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-surface-100">{vocabStatus.total_groups}</div>
              <div className="text-xs text-surface-200">Total Groups</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-warning-400">{vocabStatus.practiced}</div>
              <div className="text-xs text-surface-200">Practiced</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-success-400">{vocabStatus.mastered}</div>
              <div className="text-xs text-surface-200">Mastered</div>
            </div>
          </div>
          <div className="mt-3 progress-bar-bg">
            <div
              className="progress-bar-fill"
              style={{ width: `${vocabStatus.total_groups > 0 ? (vocabStatus.mastered / vocabStatus.total_groups) * 100 : 0}%` }}
            />
          </div>
        </div>
      )}

      {/* ── Score Trend Chart ────────────────────────────────── */}
      {chartData.length > 0 && (
        <div className="glass-card p-5">
          <h2 className="font-bold text-lg mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-accent-400" /> Score Trend
          </h2>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(30,41,59,0.95)',
                    border: '1px solid rgba(148,163,184,0.2)',
                    borderRadius: '0.75rem',
                    color: '#f1f5f9',
                  }}
                />
                <Legend />
                {Object.entries(SCORE_COLORS).map(([key, color]) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={color}
                    strokeWidth={2}
                    dot={{ fill: color, r: 4 }}
                    name={key.charAt(0).toUpperCase() + key.slice(1)}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {chartData.length === 0 && (
        <div className="glass-card p-8 text-center">
          <BarChart3 className="w-10 h-10 text-surface-700 mx-auto mb-3" />
          <p className="text-surface-200">Complete mock interviews to see your score trends here.</p>
        </div>
      )}

      {/* ── Interview History ────────────────────────────────── */}
      {interviews.length > 0 && (
        <div className="glass-card p-5">
          <h2 className="font-bold text-lg mb-3 flex items-center gap-2">
            <Trophy className="w-5 h-5 text-accent-400" /> Interview History
          </h2>
          <div className="space-y-2">
            {interviews.map((intv) => (
              <div key={intv.id} className="glass-card-light p-3 flex items-center justify-between">
                <div>
                  <span className="text-sm font-medium">Day {intv.day_number}</span>
                  <span className="badge badge-neutral text-[10px] ml-2">{intv.interview_type}</span>
                </div>
                <div className="flex items-center gap-3">
                  {intv.scores_json?.overall && (
                    <span className="text-sm font-bold text-primary-400">
                      {intv.scores_json.overall}/10
                    </span>
                  )}
                  <span className="text-xs text-surface-200">
                    {intv.created_at ? new Date(intv.created_at).toLocaleDateString() : ''}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Comparison CTA ───────────────────────────────────── */}
      <Link to="/comparison" className="block">
        <div className="glass-card p-5 border border-accent-500/20 hover:border-accent-500/40 transition-all text-center">
          <Trophy className="w-8 h-8 text-accent-400 mx-auto mb-2" />
          <h3 className="font-bold">Day 1 vs Day 30 Comparison</h3>
          <p className="text-sm text-surface-200 mt-1">See how far you've come</p>
        </div>
      </Link>
    </div>
  )
}
