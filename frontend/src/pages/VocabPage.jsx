import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { vocabAPI, progressAPI } from '../api/client'
import { useToast } from '../context/ToastContext.jsx'
import {
  ChevronLeft, BookOpen, CheckCircle, Star, Send, Loader2, RefreshCw
} from 'lucide-react'

function VocabCard({ group, onPractice, onCheckMastered }) {
  const [sentence, setSentence] = useState('')
  const [loading, setLoading] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const [status, setStatus] = useState('not_started')

  const handlePractice = async () => {
    if (!sentence.trim()) return
    setLoading(true)
    setFeedback(null)
    try {
      const res = await onCheckMastered(group.id, sentence)
      setFeedback(res.feedback)
      setStatus(res.status)
      if (res.is_mastered) {
        setStatus('mastered')
      }
    } catch {
      // Fallback to simple practice
      await onPractice(group.id, sentence)
      setStatus('practiced')
      setFeedback('Sentence saved! Keep practicing to master this group.')
    }
    setLoading(false)
  }

  return (
    <div className="glass-card p-5 space-y-3">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-bold text-lg">{group.headword}</h3>
          <div className="flex flex-wrap gap-1.5 mt-1.5">
            {group.phrases.map((phrase, i) => (
              <span key={i} className="badge badge-info text-[11px]">{phrase}</span>
            ))}
          </div>
        </div>
        <div>
          {status === 'mastered' ? (
            <span className="badge badge-success"><Star className="w-3 h-3" /> Mastered</span>
          ) : status === 'practiced' ? (
            <span className="badge badge-warning"><CheckCircle className="w-3 h-3" /> Practiced</span>
          ) : (
            <span className="badge badge-neutral">New</span>
          )}
        </div>
      </div>

      {/* Examples */}
      <div className="space-y-1">
        {group.example_sentences.map((ex, i) => (
          <p key={i} className="text-sm text-surface-200 italic">"{ex}"</p>
        ))}
      </div>

      {/* Practice input */}
      <div className="pt-2 border-t border-white/5">
        <label className="text-xs font-medium text-surface-200 mb-1 block">
          Write your own sentence using this word group:
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            className="input-field flex-1"
            placeholder={`Use "${group.headword}" in a sentence...`}
            value={sentence}
            onChange={(e) => setSentence(e.target.value)}
            disabled={loading}
            onKeyDown={(e) => e.key === 'Enter' && handlePractice()}
          />
          <button
            onClick={handlePractice}
            disabled={loading || !sentence.trim()}
            className="btn-primary flex items-center gap-1 shrink-0"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>

        {feedback && (
          <div className={`mt-2 p-3 rounded-lg text-sm ${
            status === 'mastered'
              ? 'bg-success-500/10 border border-success-500/20 text-success-400'
              : 'bg-primary-500/10 border border-primary-500/20 text-primary-400'
          }`}>
            {feedback}
          </div>
        )}
      </div>
    </div>
  )
}

export default function VocabPage() {
  const { dayNumber } = useParams()
  const dayNum = parseInt(dayNumber)
  const { addToast } = useToast()

  const [groups, setGroups] = useState([])
  const [reviewGroups, setReviewGroups] = useState([])
  const [loading, setLoading] = useState(true)
  const [showReview, setShowReview] = useState(false)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      vocabAPI.getForDay(dayNum),
      vocabAPI.getReview(),
    ]).then(([groupsRes, reviewRes]) => {
      setGroups(groupsRes.data)
      setReviewGroups(reviewRes.data)
    }).catch(() => {
      addToast('Failed to load vocabulary', 'error')
    }).finally(() => setLoading(false))
  }, [dayNum])

  const handlePractice = async (groupId, sentence) => {
    const res = await vocabAPI.practice({ group_id: groupId, user_sentence: sentence })
    await progressAPI.completeModule({ day_number: dayNum, module: 'vocabulary' })
    return res.data
  }

  const handleCheckMastered = async (groupId, sentence) => {
    const res = await vocabAPI.checkMastered({ group_id: groupId, user_sentence: sentence })
    await progressAPI.completeModule({ day_number: dayNum, module: 'vocabulary' })
    return res.data
  }

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto space-y-4">
        {[1,2,3].map(i => <div key={i} className="skeleton h-40 w-full" />)}
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* ── Header ─────────────────────────────────────────────── */}
      <div>
        <Link to={`/day/${dayNum}`} className="inline-flex items-center gap-1 text-sm text-surface-200 hover:text-primary-400 mb-3 transition-colors">
          <ChevronLeft className="w-4 h-4" /> Day {dayNum}
        </Link>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-primary-400" />
          Vocabulary Builder
        </h1>
        <p className="text-surface-200 mt-1 text-sm">
          {groups.length} word groups · Write sentences to practice and master each group
        </p>
      </div>

      {/* ── Review queue ───────────────────────────────────────── */}
      {reviewGroups.length > 0 && (
        <div>
          <button
            onClick={() => setShowReview(!showReview)}
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <RefreshCw className="w-4 h-4" />
            Review Queue ({reviewGroups.length} groups from earlier days)
          </button>
          {showReview && (
            <div className="mt-3 space-y-4">
              <p className="text-xs text-surface-200">These groups from earlier days need another practice round:</p>
              {reviewGroups.map((g) => (
                <VocabCard
                  key={g.id}
                  group={g}
                  onPractice={handlePractice}
                  onCheckMastered={handleCheckMastered}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Today's groups ─────────────────────────────────────── */}
      <div className="space-y-4">
        {groups.map((g) => (
          <VocabCard
            key={g.id}
            group={g}
            onPractice={handlePractice}
            onCheckMastered={handleCheckMastered}
          />
        ))}
      </div>
    </div>
  )
}
