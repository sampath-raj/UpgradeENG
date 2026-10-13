import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { writingAPI, curriculumAPI, progressAPI } from '../api/client'
import { useToast } from '../context/ToastContext.jsx'
import { ChevronLeft, Send, Loader2, Clock, FileText } from 'lucide-react'

export default function WritingPage() {
  const { dayNumber } = useParams()
  const dayNum = parseInt(dayNumber)
  const { addToast } = useToast()

  const [day, setDay] = useState(null)
  const [text, setText] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [correction, setCorrection] = useState(null)
  const [history, setHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)

  useEffect(() => {
    curriculumAPI.getDay(dayNum).then(res => setDay(res.data)).catch(() => {})
    writingAPI.history(dayNum).then(res => setHistory(res.data)).catch(() => {})
  }, [dayNum])

  const handleSubmit = async () => {
    if (text.trim().length < 10) {
      addToast('Please write at least 10 characters', 'error')
      return
    }
    setSubmitting(true)
    setCorrection(null)
    try {
      const res = await writingAPI.submit({ day_number: dayNum, text })
      setCorrection(res.data)
      // Mark module complete
      await progressAPI.completeModule({ day_number: dayNum, module: 'writing' })
      addToast('Writing corrected! ✍️', 'success')
      // Refresh history
      writingAPI.history(dayNum).then(r => setHistory(r.data)).catch(() => {})
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to submit. Your text is saved — try again.', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const wordCount = text.trim().split(/\s+/).filter(Boolean).length

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* ── Header ─────────────────────────────────────────────── */}
      <div>
        <Link to={`/day/${dayNum}`} className="inline-flex items-center gap-1 text-sm text-surface-200 hover:text-primary-400 mb-3 transition-colors">
          <ChevronLeft className="w-4 h-4" /> Day {dayNum}
        </Link>
        <h1 className="text-2xl font-bold">Writing Practice</h1>
        {day && (
          <p className="text-surface-200 mt-1 text-sm">{day.grammar_topic} · Day {dayNum}</p>
        )}
      </div>

      {/* ── Prompt ──────────────────────────────────────────────── */}
      {day && (
        <div className="glass-card p-5">
          <h2 className="text-sm font-bold text-primary-400 mb-2">TODAY'S PROMPT</h2>
          <p className="leading-relaxed">{day.writing_prompt}</p>
        </div>
      )}

      {/* ── Text input ─────────────────────────────────────────── */}
      <div className="glass-card p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-bold">Your Response</h2>
          <span className={`text-xs ${wordCount >= 150 ? 'text-success-400' : 'text-surface-200'}`}>
            {wordCount} / 150-200 words
          </span>
        </div>
        <textarea
          className="input-field min-h-[180px]"
          placeholder="Write your response here..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={submitting}
        />
        <div className="flex justify-end">
          <button
            onClick={handleSubmit}
            disabled={submitting || text.trim().length < 10}
            className="btn-primary flex items-center gap-2"
          >
            {submitting ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</>
            ) : (
              <><Send className="w-4 h-4" /> Submit for Correction</>
            )}
          </button>
        </div>
      </div>

      {/* ── Correction Result ──────────────────────────────────── */}
      {correction && correction.blocks && (
        <div className="space-y-3">
          <h2 className="text-lg font-bold">AI Feedback</h2>
          {correction.blocks.map((block, i) => (
            <div key={i} className="correction-block">
              <div className="space-y-2">
                <div>
                  <span className="text-xs font-bold text-surface-200 uppercase">Original</span>
                  <p className="correction-original text-sm mt-0.5">{block.original}</p>
                </div>
                <div>
                  <span className="text-xs font-bold text-surface-200 uppercase">Corrected</span>
                  <p className="correction-fixed text-sm mt-0.5">{block.corrected}</p>
                </div>
                <div>
                  <span className="text-xs font-bold text-surface-200 uppercase">More Natural</span>
                  <p className="correction-natural text-sm mt-0.5">{block.natural}</p>
                </div>
                <p className="correction-reason">💡 {block.reason}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── History toggle ─────────────────────────────────────── */}
      {history.length > 0 && (
        <div>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <Clock className="w-4 h-4" />
            {showHistory ? 'Hide' : 'Show'} Previous Submissions ({history.length})
          </button>

          {showHistory && (
            <div className="mt-3 space-y-3">
              {history.map((item) => (
                <div key={item.id} className="glass-card-light p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-surface-200">
                      {new Date(item.created_at).toLocaleDateString()} · {new Date(item.created_at).toLocaleTimeString()}
                    </span>
                    {item.correction_json ? (
                      <span className="badge badge-success text-[10px]">Corrected</span>
                    ) : (
                      <span className="badge badge-warning text-[10px]">Pending</span>
                    )}
                  </div>
                  <p className="text-sm text-surface-200 line-clamp-3">{item.original_text}</p>
                  {item.correction_json?.blocks && (
                    <p className="text-xs text-success-400 mt-2">
                      {item.correction_json.blocks.length} corrections
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
