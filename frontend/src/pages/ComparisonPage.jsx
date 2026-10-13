import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { progressAPI } from '../api/client'
import { Trophy, ChevronLeft, MicOff, ArrowRight } from 'lucide-react'

function ScoreComparison({ label, baseline, final, note }) {
  const hasBaseline = baseline !== null && baseline !== undefined
  const hasFinal = final !== null && final !== undefined
  const diff = hasBaseline && hasFinal ? final - baseline : null

  if (!hasBaseline && !hasFinal) {
    return (
      <div className="flex items-center gap-3 py-2">
        <span className="text-sm w-28 shrink-0">{label}</span>
        <span className="text-xs text-warning-400 flex items-center gap-1">
          <MicOff className="w-3 h-3" /> {note || 'voice mode required'}
        </span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 py-2">
      <span className="text-sm w-28 shrink-0">{label}</span>
      <div className="flex items-center gap-2 flex-1">
        <span className={`text-lg font-bold ${hasBaseline ? 'text-surface-100' : 'text-surface-700'}`}>
          {hasBaseline ? baseline : '—'}
        </span>
        <ArrowRight className="w-4 h-4 text-surface-200" />
        <span className={`text-lg font-bold ${hasFinal ? 'text-surface-100' : 'text-surface-700'}`}>
          {hasFinal ? final : '—'}
        </span>
        {diff !== null && (
          <span className={`text-sm font-bold ml-2 ${
            diff > 0 ? 'text-success-400' : diff < 0 ? 'text-danger-400' : 'text-surface-200'
          }`}>
            {diff > 0 ? `+${diff}` : diff === 0 ? '±0' : diff}
          </span>
        )}
      </div>
    </div>
  )
}

export default function ComparisonPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    progressAPI.comparison()
      .then(res => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-4">
        <div className="skeleton h-8 w-48" />
        <div className="skeleton h-60 w-full" />
      </div>
    )
  }

  const baseline = data?.baseline
  const final_ = data?.final
  const bScores = baseline?.scores || {}
  const fScores = final_?.scores || {}

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <Link to="/progress" className="inline-flex items-center gap-1 text-sm text-surface-200 hover:text-primary-400 mb-3 transition-colors">
          <ChevronLeft className="w-4 h-4" /> Progress
        </Link>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Trophy className="w-6 h-6 text-accent-400" />
          Day 1 vs Day 30 Comparison
        </h1>
        <p className="text-surface-200 mt-1 text-sm">
          See how your interview performance has changed over the program
        </p>
      </div>

      {!baseline && !final_ && (
        <div className="glass-card p-8 text-center">
          <Trophy className="w-12 h-12 text-surface-700 mx-auto mb-3" />
          <h2 className="text-lg font-bold">No Comparison Available Yet</h2>
          <p className="text-surface-200 mt-2">
            Complete the baseline interview (Day 0) and the final interview (Day 30) to see your comparison.
          </p>
          <Link to="/day/0/interview" className="btn-primary inline-block mt-4">
            Take Baseline Interview
          </Link>
        </div>
      )}

      {(baseline || final_) && (
        <>
          {/* ── Score comparison ────────────────────────────────── */}
          <div className="glass-card p-6">
            <h2 className="font-bold text-lg mb-4">Score Comparison</h2>
            <div className="grid grid-cols-3 gap-2 text-center text-xs text-surface-200 mb-2 font-bold">
              <div className="text-left pl-28">Dimension</div>
              <div>Baseline → Final</div>
              <div>Change</div>
            </div>
            <div className="divide-y divide-white/5">
              <ScoreComparison label="Grammar" baseline={bScores.grammar} final={fScores.grammar} />
              <ScoreComparison label="Vocabulary" baseline={bScores.vocabulary} final={fScores.vocabulary} />
              <ScoreComparison label="Fluency" baseline={bScores.fluency} final={fScores.fluency} />
              <ScoreComparison label="Pronunciation" baseline={bScores.pronunciation} final={fScores.pronunciation} note={bScores.pronunciation_note} />
              <ScoreComparison label="Confidence" baseline={bScores.confidence} final={fScores.confidence} note={bScores.confidence_note} />
              <ScoreComparison label="Structure" baseline={bScores.structure} final={fScores.structure} />
              <ScoreComparison label="Overall" baseline={bScores.overall} final={fScores.overall} />
            </div>
          </div>

          {/* ── Feedback comparison ────────────────────────────── */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="glass-card p-5">
              <h3 className="font-bold mb-2 flex items-center gap-2">
                <span className="badge badge-info">Baseline</span> Feedback
              </h3>
              <p className="text-sm text-surface-200 leading-relaxed whitespace-pre-wrap">
                {baseline?.feedback || 'No baseline interview yet'}
              </p>
            </div>
            <div className="glass-card p-5">
              <h3 className="font-bold mb-2 flex items-center gap-2">
                <span className="badge badge-success">Final</span> Feedback
              </h3>
              <p className="text-sm text-surface-200 leading-relaxed whitespace-pre-wrap">
                {final_?.feedback || 'No final interview yet'}
              </p>
            </div>
          </div>

          {/* ── Transcript comparison ──────────────────────────── */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="glass-card p-5">
              <h3 className="font-bold mb-3 flex items-center gap-2">
                <span className="badge badge-info">Baseline</span> Transcript
              </h3>
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {baseline?.transcript?.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`text-xs p-2 rounded-lg max-w-[85%] ${
                      msg.role === 'user'
                        ? 'bg-primary-600/20 text-primary-300'
                        : 'bg-surface-800/50 text-surface-200'
                    }`}>
                      {msg.content}
                    </div>
                  </div>
                )) || <p className="text-sm text-surface-700">Not available</p>}
              </div>
            </div>
            <div className="glass-card p-5">
              <h3 className="font-bold mb-3 flex items-center gap-2">
                <span className="badge badge-success">Final</span> Transcript
              </h3>
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {final_?.transcript?.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`text-xs p-2 rounded-lg max-w-[85%] ${
                      msg.role === 'user'
                        ? 'bg-success-600/20 text-success-300'
                        : 'bg-surface-800/50 text-surface-200'
                    }`}>
                      {msg.content}
                    </div>
                  </div>
                )) || <p className="text-sm text-surface-700">Not available</p>}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
