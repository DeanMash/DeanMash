import { useEffect, useMemo, useState } from 'react'
import { getIndustry, type IndustryId } from '../data/industries'
import { buildSlots, qualifyLead, type TimeSlot } from '../lib/booking'

type Message = {
  id: string
  role: 'ai' | 'caller'
  text: string
}

type Props = {
  industryId: IndustryId
  onIndustryChange: (id: IndustryId) => void
}

export function Demo({ industryId, onIndustryChange }: Props) {
  const industry = useMemo(() => getIndustry(industryId), [industryId])
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [messages, setMessages] = useState<Message[]>([])
  const [callerName, setCallerName] = useState('')
  const [phone, setPhone] = useState('')
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null)
  const [booked, setBooked] = useState(false)

  const slots = useMemo(() => buildSlots(industry), [industry])
  const question = industry.questions[step]
  const finishedQuestions = step >= industry.questions.length

  const result = useMemo(() => {
    if (!finishedQuestions) return null
    return qualifyLead(industry, answers)
  }, [answers, finishedQuestions, industry])

  useEffect(() => {
    setStep(0)
    setAnswers({})
    setSelectedSlot(null)
    setBooked(false)
    setMessages([
      {
        id: 'greet',
        role: 'ai',
        text: industry.greeting,
      },
      {
        id: 'q0',
        role: 'ai',
        text: industry.questions[0].prompt,
      },
    ])
  }, [industry])

  useEffect(() => {
    if (result?.recommendedSlot) {
      setSelectedSlot(result.recommendedSlot)
    }
  }, [result])

  function chooseOption(value: string, label: string) {
    if (!question) return
    const nextAnswers = { ...answers, [question.id]: value }
    setAnswers(nextAnswers)
    setMessages((prev) => [
      ...prev,
      { id: `a-${question.id}`, role: 'caller', text: label },
    ])

    const nextStep = step + 1
    if (nextStep < industry.questions.length) {
      const nextQuestion = industry.questions[nextStep]
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { id: `q-${nextQuestion.id}`, role: 'ai', text: nextQuestion.prompt },
        ])
        setStep(nextStep)
      }, 280)
      return
    }

    setTimeout(() => {
      const outcome = qualifyLead(industry, nextAnswers)
      setMessages((prev) => [
        ...prev,
        {
          id: 'outcome',
          role: 'ai',
          text: `${outcome.message} I can hold ${outcome.recommendedSlot ? `${outcome.recommendedSlot.dayLabel} at ${outcome.recommendedSlot.label}` : 'a callback from the team'}.`,
        },
      ])
      setStep(nextStep)
    }, 280)
  }

  function resetDemo() {
    setStep(0)
    setAnswers({})
    setSelectedSlot(null)
    setBooked(false)
    setCallerName('')
    setPhone('')
    setMessages([
      { id: 'greet', role: 'ai', text: industry.greeting },
      { id: 'q0', role: 'ai', text: industry.questions[0].prompt },
    ])
  }

  function confirmBooking() {
    if (!selectedSlot || !callerName.trim() || !phone.trim()) return
    setBooked(true)
    setMessages((prev) => [
      ...prev,
      {
        id: `booked-${selectedSlot.id}`,
        role: 'ai',
        text: `Done, ${callerName.split(' ')[0]}. You’re booked for ${selectedSlot.dayLabel} at ${selectedSlot.label}. A confirmation text is on its way to ${phone}.`,
      },
    ])
  }

  return (
    <section className="section" id="demo">
      <div className="container">
        <div className="section-head">
          <p className="eyebrow">Live demo</p>
          <h2>Run an after-hours call for {industry.shortName.toLowerCase()}.</h2>
          <p>
            Answer as the caller. Deskline qualifies the lead and offers the best
            working-hours appointment — usually the following open day.
          </p>
        </div>

        <div className="demo-shell">
          <div className="phone-frame demo-stage">
            <div className="phone-bar">
              <span className="live-dot">Live AI line</span>
              <span>{industry.workingHours.label}</span>
            </div>
            <div className="transcript" aria-live="polite">
              {messages.map((message) => (
                <div key={message.id} className={`bubble ${message.role}`}>
                  <strong>{message.role === 'ai' ? 'Deskline' : 'Caller'}</strong>
                  {message.text}
                </div>
              ))}
            </div>

            {!finishedQuestions && question && (
              <div className="option-list" aria-label="Caller responses">
                {question.options.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => chooseOption(option.value, option.label)}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="panel demo-stage">
            <div className="field">
              <label htmlFor="industry">Industry script</label>
              <select
                id="industry"
                value={industryId}
                onChange={(event) => onIndustryChange(event.target.value as IndustryId)}
              >
                <option value="dental">Dental surgeries</option>
                <option value="plumber">Plumbers</option>
                <option value="medspa">Med spas</option>
              </select>
            </div>

            {!result && (
              <>
                <p className="eyebrow">In progress</p>
                <h3>Waiting for qualification answers</h3>
                <p style={{ color: 'var(--sand-dim)' }}>
                  Choose responses in the phone on the left. Deskline scores urgency,
                  fit, and timing before offering diary space.
                </p>
                <div className="result-meta">
                  <div className="meta-row">
                    <span>Services covered</span>
                    <strong>{industry.services.length}</strong>
                  </div>
                  <div className="meta-row">
                    <span>Slot length</span>
                    <strong>{industry.slotMinutes} min</strong>
                  </div>
                  <div className="meta-row">
                    <span>Booking window</span>
                    <strong>{industry.workingHours.label}</strong>
                  </div>
                </div>
              </>
            )}

            {result && (
              <>
                <span className={`badge ${result.status}`}>{result.status}</span>
                <h3>{result.message}</h3>
                <p style={{ color: 'var(--sand-dim)' }}>
                  Score {result.score}/100
                  {result.urgent ? ' · Priority triage' : ' · Standard lead'}
                </p>

                {result.recommendedSlot && (
                  <>
                    <div className="result-meta">
                      <div className="meta-row">
                        <span>Recommended</span>
                        <strong>
                          {result.recommendedSlot.dayLabel} · {result.recommendedSlot.label}
                        </strong>
                      </div>
                    </div>

                    <p style={{ color: 'var(--sand-dim)', marginBottom: '0.5rem' }}>
                      Choose a working-hours slot
                    </p>
                    <div className="slot-grid">
                      {slots.map((slot) => (
                        <button
                          key={slot.id}
                          type="button"
                          className={`slot${selectedSlot?.id === slot.id ? ' selected' : ''}`}
                          onClick={() => setSelectedSlot(slot)}
                          disabled={booked}
                        >
                          <small>{slot.dayLabel}</small>
                          <strong>{slot.label}</strong>
                        </button>
                      ))}
                    </div>

                    {!booked ? (
                      <div className="lead-form">
                        <div className="field">
                          <label htmlFor="name">Caller name</label>
                          <input
                            id="name"
                            value={callerName}
                            onChange={(event) => setCallerName(event.target.value)}
                            placeholder="Alex Morgan"
                          />
                        </div>
                        <div className="field">
                          <label htmlFor="phone">Mobile for confirmation</label>
                          <input
                            id="phone"
                            value={phone}
                            onChange={(event) => setPhone(event.target.value)}
                            placeholder="+1 555 010 2299"
                          />
                        </div>
                        <button
                          type="button"
                          className="btn btn-teal"
                          onClick={confirmBooking}
                          disabled={!selectedSlot || !callerName.trim() || !phone.trim()}
                        >
                          Confirm appointment
                        </button>
                      </div>
                    ) : (
                      <div className="success-note">
                        Appointment held for {selectedSlot?.dayLabel} at{' '}
                        {selectedSlot?.label}. Practice notified for morning review.
                      </div>
                    )}
                  </>
                )}

                {!result.recommendedSlot && (
                  <p style={{ color: 'var(--sand-dim)', marginTop: '1rem' }}>
                    This lead stays as a warm callback — still captured, never lost to
                    voicemail.
                  </p>
                )}
              </>
            )}

            <div style={{ marginTop: '1.4rem' }}>
              <button type="button" className="btn btn-ghost" onClick={resetDemo}>
                Restart call
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
