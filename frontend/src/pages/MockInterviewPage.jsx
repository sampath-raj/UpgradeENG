import { useState, useEffect, useRef } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { interviewAPI, progressAPI } from '../api/client'
import { useAuth } from '../context/AuthContext.jsx'
import { useToast } from '../context/ToastContext.jsx'
import {
  ChevronLeft, Send, Loader2, Trophy, AlertTriangle, Mic, MicOff
} from 'lucide-react'

function ScoreBar({ label, score, maxScore = 10, note }) {
  if (score === null || score === undefined) {
    return (
      <div className="flex items-center gap-3">
        <span className="text-sm w-28 shrink-0">{label}</span>
        <div className="flex-1 progress-bar-bg">
          <div className="h-full bg-surface-700 rounded-full" style={{ width: '0%' }} />
        </div>
        <span className="text-xs text-warning-400 w-32 text-right flex items-center gap-1">
          <MicOff className="w-3 h-3" /> {note || 'voice mode required'}
        </span>
      </div>
    )
  }
  const pct = (score / maxScore) * 100
  const color = score >= 7 ? 'bg-success-500' : score >= 5 ? 'bg-warning-500' : 'bg-danger-500'
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm w-28 shrink-0">{label}</span>
      <div className="flex-1 progress-bar-bg">
        <div className={`h-full rounded-full transition-all duration-700 ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm font-bold w-10 text-right">{score}/10</span>
    </div>
  )
}

export default function MockInterviewPage() {
  const { dayNumber } = useParams()
  const dayNum = parseInt(dayNumber)
  const { user, refreshUser } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const messagesEndRef = useRef(null)

  const [phase, setPhase] = useState('ready') // ready | interview | scoring | debrief
  const [interviewId, setInterviewId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [result, setResult] = useState(null)

  // Determine interview type
  const interviewType = dayNum === 0 ? 'baseline' : dayNum === 30 ? 'final' : 'weekly_checkpoint'

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startInterview = async () => {
    setSending(true)
    try {
      const res = await interviewAPI.start({
        day_number: dayNum,
        interview_type: interviewType,
      })
      setInterviewId(res.data.interview_id)
      setMessages([{ role: 'assistant', content: res.data.first_question }])
      setPhase('interview')
    } catch (err) {
      addToast('Failed to start interview', 'error')
    }
    setSending(false)
  }

  const sendAnswer = async () => {
    if (!input.trim() || sending) return
    const answer = input.trim()
    setMessages(prev => [...prev, { role: 'user', content: answer }])
    setInput('')
    setSending(true)

    try {
      const res = await interviewAPI.respond({
        interview_id: interviewId,
        user_answer: answer,
      })

      if (res.data.is_complete) {
        // Interview done — get scores
        setPhase('scoring')
        const finishRes = await interviewAPI.finish({ interview_id: interviewId })
        setResult(finishRes.data)
        setPhase('debrief')
        // Mark module complete
        await progressAPI.completeModule({ day_number: dayNum, module: 'mock_interview' })
        refreshUser()
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: res.data.next_question }])
      }
    } catch (err) {
      addToast('Failed to send response. Try again.', 'error')
    }
    setSending(false)
  }

  // ── Ready phase ─────────────────────────────────────────────
  if (phase === 'ready') {
    return (
      <div className="max-w-2xl mx-auto flex items-center justify-center" style={{ minHeight: 'calc(100vh - 200px)' }}>
        <div className="glass-card p-8 text-center space-y-6 w-full">
          <div>
            <Trophy className="w-16 h-16 text-accent-400 mx-auto mb-4" />
            <h1 className="text-2xl font-bold">
              {interviewType === 'baseline' ? 'Baseline Interview' :
               interviewType === 'final' ? 'Final Interview — Day 30' :
               `Mock Interview — Day ${dayNum}`}
            </h1>
            <p className="text-surface-200 mt-2 max-w-sm mx-auto">
              {interviewType === 'baseline'
                ? 'This baseline interview measures your starting point. Answer naturally — no coaching will be given during the interview.'
                : interviewType === 'final'
                  ? 'This is your final interview! It will be compared against your Day 0 baseline.'
                  : 'A full mock interview with HR and technical questions. No corrections until the debrief.'}
            </p>
          </div>
          <div className="glass-card-light p-4 text-left space-y-2">
            <div className="flex items-start gap-2 text-sm">
              <AlertTriangle className="w-4 h-4 text-warning-400 mt-0.5 shrink-0" />
              <span className="text-surface-200">The interviewer will NOT correct you during the interview — only in the debrief after.</span>
            </div>
            <div className="flex items-start gap-2 text-sm">
              <Trophy className="w-4 h-4 text-accent-400 mt-0.5 shrink-0" />
              <span className="text-surface-200">You'll be scored on 7 dimensions: Grammar, Vocabulary, Fluency, Pronunciation*, Confidence*, Structure, Overall.</span>
            </div>
          </div>
          <div className="flex gap-3 justify-center">
            <Link to={dayNum === 0 ? '/' : `/day/${dayNum}`} className="btn-secondary">
              <ChevronLeft className="w-4 h-4 inline mr-1" /> Back
            </Link>
            <button onClick={startInterview} className="btn-primary" disabled={sending}>
              {sending ? 'Starting...' : 'Begin Interview'}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ── Scoring phase ───────────────────────────────────────────
  if (phase === 'scoring') {
    return (
      <div className="max-w-2xl mx-auto flex items-center justify-center" style={{ minHeight: 'calc(100vh - 200px)' }}>
        <div className="glass-card p-8 text-center space-y-4">
          <Loader2 className="w-12 h-12 animate-spin text-primary-400 mx-auto" />
          <h2 className="text-xl font-bold">Scoring Your Interview</h2>
          <p className="text-surface-200">The AI is evaluating your responses across 7 dimensions...</p>
        </div>
      </div>
    )
  }

  // ── Debrief phase ───────────────────────────────────────────
  if (phase === 'debrief' && result) {
    const s = result.scores
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Trophy className="w-6 h-6 text-accent-400" /> Interview Debrief
        </h1>

        {/* Scores */}
        <div className="glass-card p-6 space-y-4">
          <h2 className="font-bold text-lg mb-2">Your Scores</h2>
          <ScoreBar label="Grammar" score={s.grammar} />
          <ScoreBar label="Vocabulary" score={s.vocabulary} />
          <ScoreBar label="Fluency" score={s.fluency} />
          <ScoreBar label="Pronunciation" score={s.pronunciation} note={s.pronunciation_note} />
          <ScoreBar label="Confidence" score={s.confidence} note={s.confidence_note} />
          <ScoreBar label="Structure" score={s.structure} />
          <ScoreBar label="Overall" score={s.overall} />
        </div>

        {/* Feedback */}
        <div className="glass-card p-6">
          <h2 className="font-bold text-lg mb-3">Detailed Feedback</h2>
          <p className="text-surface-200 leading-relaxed whitespace-pre-wrap">{result.feedback}</p>
        </div>

        {/* Transcript */}
        <div className="glass-card p-6">
          <h2 className="font-bold text-lg mb-3">Interview Transcript</h2>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {result.transcript.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex gap-3 justify-center">
          <Link to={dayNum === 0 ? '/' : `/day/${dayNum}`} className="btn-secondary">
            Back to {dayNum === 0 ? 'Dashboard' : `Day ${dayNum}`}
          </Link>
          <Link to="/progress" className="btn-primary">View Progress →</Link>
        </div>
      </div>
    )
  }

  // ── Interview phase ─────────────────────────────────────────
  return (
    <div className="max-w-3xl mx-auto flex flex-col" style={{ height: 'calc(100vh - 120px)' }}>
      <div className="mb-3 shrink-0 flex items-center justify-between">
        <h1 className="text-lg font-bold flex items-center gap-2">
          <Trophy className="w-5 h-5 text-accent-400" />
          Mock Interview in Progress
        </h1>
        <span className="badge badge-warning">No corrections during interview</span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-4 pr-1">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'}>
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <div className="chat-bubble-assistant">
              <Loader2 className="w-4 h-4 animate-spin text-surface-200" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="shrink-0 flex gap-2">
        <input
          type="text"
          className="input-field flex-1"
          placeholder="Type your answer..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendAnswer()}
          disabled={sending}
          autoFocus
        />
        <button
          onClick={sendAnswer}
          disabled={sending || !input.trim()}
          className="btn-primary flex items-center gap-1"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
