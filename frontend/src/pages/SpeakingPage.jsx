import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { speakingAPI, curriculumAPI, progressAPI } from '../api/client'
import { useToast } from '../context/ToastContext.jsx'
import { ChevronLeft, Send, Loader2, MessageSquare, X } from 'lucide-react'

const MODES = [
  { value: 'intro', label: 'Self Introduction' },
  { value: 'unprepared', label: 'Unprepared Topic' },
  { value: 'interview_qs', label: 'Interview Q&A' },
  { value: 'free_chat', label: 'Free Conversation' },
]

export default function SpeakingPage() {
  const { dayNumber } = useParams()
  const dayNum = parseInt(dayNumber)
  const { addToast } = useToast()
  const messagesEndRef = useRef(null)

  const [day, setDay] = useState(null)
  const [mode, setMode] = useState('intro')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [sending, setSending] = useState(false)
  const [started, setStarted] = useState(false)

  useEffect(() => {
    curriculumAPI.getDay(dayNum).then(res => setDay(res.data)).catch(() => {})
  }, [dayNum])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startSession = async () => {
    setStarted(true)
    setSending(true)
    // Send initial greeting
    const initialMessages = [
      { role: 'user', content: `Hi, I'd like to practice ${MODES.find(m => m.value === mode)?.label.toLowerCase()}. Today's topic is: ${day?.focus_topic || 'general conversation'}` }
    ]
    try {
      const res = await speakingAPI.chat({
        day_number: dayNum,
        mode,
        messages: initialMessages,
      })
      setSessionId(res.data.session_id)
      setMessages([
        ...initialMessages,
        { role: 'assistant', content: res.data.reply },
      ])
    } catch (err) {
      addToast('Failed to start session', 'error')
      setStarted(false)
    }
    setSending(false)
  }

  const sendMessage = async () => {
    if (!input.trim() || sending) return
    const userMsg = { role: 'user', content: input.trim() }
    const updatedMessages = [...messages, userMsg]
    setMessages(updatedMessages)
    setInput('')
    setSending(true)

    try {
      const res = await speakingAPI.chat({
        day_number: dayNum,
        mode,
        messages: updatedMessages,
        session_id: sessionId,
      })
      setSessionId(res.data.session_id)
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.reply }])
    } catch (err) {
      addToast('Failed to get response. Try again.', 'error')
    }
    setSending(false)
  }

  const endSession = async () => {
    if (sessionId && messages.length > 0) {
      try {
        await speakingAPI.end({ session_id: sessionId, messages })
        await progressAPI.completeModule({ day_number: dayNum, module: 'speaking' })
        addToast('Speaking session saved! 🎤', 'success')
      } catch {
        addToast('Failed to save session', 'error')
      }
    }
    setStarted(false)
    setMessages([])
    setSessionId(null)
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col" style={{ height: 'calc(100vh - 120px)' }}>
      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="mb-4 shrink-0">
        <Link to={`/day/${dayNum}`} className="inline-flex items-center gap-1 text-sm text-surface-200 hover:text-primary-400 mb-2 transition-colors">
          <ChevronLeft className="w-4 h-4" /> Day {dayNum}
        </Link>
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-primary-400" />
            Speaking Practice
          </h1>
          {started && (
            <button onClick={endSession} className="btn-secondary text-xs flex items-center gap-1">
              <X className="w-3 h-3" /> End Session
            </button>
          )}
        </div>
      </div>

      {/* ── Mode selector (before start) ───────────────────────── */}
      {!started && (
        <div className="flex-1 flex items-center justify-center">
          <div className="glass-card p-8 w-full max-w-md text-center space-y-6">
            <div>
              <MessageSquare className="w-12 h-12 text-primary-400 mx-auto mb-3" />
              <h2 className="text-xl font-bold">Choose Practice Mode</h2>
              <p className="text-sm text-surface-200 mt-1">
                {day?.speaking_prompt?.substring(0, 100)}...
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {MODES.map(m => (
                <button
                  key={m.value}
                  onClick={() => setMode(m.value)}
                  className={`p-3 rounded-xl text-sm font-medium transition-all ${
                    mode === m.value
                      ? 'bg-primary-600/30 border border-primary-500/50 text-primary-400'
                      : 'bg-surface-800/50 border border-white/5 text-surface-200 hover:bg-white/5'
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>
            <button onClick={startSession} className="btn-primary w-full" disabled={sending}>
              {sending ? 'Starting...' : 'Start Conversation'}
            </button>
          </div>
        </div>
      )}

      {/* ── Chat area ──────────────────────────────────────────── */}
      {started && (
        <>
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
              placeholder="Type your response..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              disabled={sending}
              autoFocus
            />
            <button
              onClick={sendMessage}
              disabled={sending || !input.trim()}
              className="btn-primary flex items-center gap-1"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </>
      )}
    </div>
  )
}
