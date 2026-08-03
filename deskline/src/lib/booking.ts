import type { Industry } from '../data/industries'

export type TimeSlot = {
  id: string
  start: Date
  label: string
  dayLabel: string
}

function isWeekend(date: Date): boolean {
  const day = date.getDay()
  return day === 0 || day === 6
}

function startOfDay(date: Date): Date {
  const next = new Date(date)
  next.setHours(0, 0, 0, 0)
  return next
}

function addDays(date: Date, days: number): Date {
  const next = new Date(date)
  next.setDate(next.getDate() + days)
  return next
}

function formatDay(date: Date): string {
  return date.toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  })
}

/** Next working day on or after `from`, respecting industry hours. */
export function nextWorkingDay(from: Date, industry: Industry): Date {
  let cursor = startOfDay(from)
  // If call is after close today, start looking from tomorrow.
  const nowHour = from.getHours() + from.getMinutes() / 60
  if (nowHour >= industry.workingHours.end) {
    cursor = addDays(cursor, 1)
  }

  for (let i = 0; i < 14; i += 1) {
    const candidate = addDays(cursor, i)
    const day = candidate.getDay()
    if (industry.id === 'medspa') {
      // Tue–Sat
      if (day >= 2 && day <= 6) return candidate
      continue
    }
    if (industry.id === 'plumber') {
      // Mon–Sat
      if (day >= 1 && day <= 6) return candidate
      continue
    }
    // Dental: Mon–Fri
    if (!isWeekend(candidate)) return candidate
  }

  return addDays(cursor, 1)
}

export function buildSlots(industry: Industry, from = new Date(), count = 6): TimeSlot[] {
  const day = nextWorkingDay(from, industry)
  const slots: TimeSlot[] = []
  const { start, end } = industry.workingHours
  const step = industry.slotMinutes

  for (let hour = start; hour < end && slots.length < count; hour += step / 60) {
    const startDate = new Date(day)
    const whole = Math.floor(hour)
    const minutes = Math.round((hour - whole) * 60)
    startDate.setHours(whole, minutes, 0, 0)
    slots.push({
      id: startDate.toISOString(),
      start: startDate,
      label: formatTime(startDate),
      dayLabel: formatDay(startDate),
    })
  }

  // Prefer morning first for urgent, but always return earliest working slots.
  return slots
}

export type QualificationResult = {
  score: number
  urgent: boolean
  status: 'qualified' | 'triage' | 'callback'
  message: string
  recommendedSlot: TimeSlot | null
}

export function qualifyLead(
  industry: Industry,
  answers: Record<string, string>,
  from = new Date(),
): QualificationResult {
  let score = 0
  let urgent = false

  for (const question of industry.questions) {
    const value = answers[question.id]
    const option = question.options.find((item) => item.value === value)
    if (!option) continue
    score += option.score
    if (option.urgency) urgent = true
  }

  const slots = buildSlots(industry, from)
  const recommendedSlot = urgent ? slots[0] ?? null : slots[Math.min(2, slots.length - 1)] ?? slots[0] ?? null

  if (urgent || score >= 70) {
    return {
      score,
      urgent: true,
      status: 'triage',
      message: industry.outcomes.triage,
      recommendedSlot,
    }
  }

  if (score >= 45) {
    return {
      score,
      urgent: false,
      status: 'qualified',
      message: industry.outcomes.qualified,
      recommendedSlot,
    }
  }

  return {
    score,
    urgent: false,
    status: 'callback',
    message: industry.outcomes.callback,
    recommendedSlot: null,
  }
}
