export type IndustryId = 'dental' | 'plumber' | 'medspa'

export type QualQuestion = {
  id: string
  prompt: string
  options: { label: string; value: string; score: number; urgency?: boolean }[]
}

export type Industry = {
  id: IndustryId
  name: string
  shortName: string
  headline: string
  summary: string
  heroLine: string
  image: string
  imageAlt: string
  greeting: string
  services: string[]
  workingHours: { start: number; end: number; label: string }
  slotMinutes: number
  questions: QualQuestion[]
  outcomes: {
    qualified: string
    triage: string
    callback: string
  }
}

export const industries: Industry[] = [
  {
    id: 'dental',
    name: 'Dental surgeries',
    shortName: 'Dental',
    headline: 'Toothache at 7pm should still become tomorrow’s chair time.',
    summary:
      'Deskline greets every missed call, screens for pain and new-patient fit, then locks a slot in your diary for the next open day.',
    heroLine: 'Built for busy practices that lose new patients after closing.',
    image:
      'https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1800&q=80',
    imageAlt: 'Modern dental treatment room at dusk',
    greeting:
      'Thanks for calling Brightside Dental. You’ve reached our after-hours desk. I’m Deskline — I can help with emergencies and book you in for the next available appointment.',
    services: [
      'New patient exam',
      'Emergency pain visit',
      'Hygiene / scale & polish',
      'Cosmetic consult',
      'Invisalign consult',
    ],
    workingHours: { start: 9, end: 17, label: 'Mon–Fri · 9:00–17:00' },
    slotMinutes: 30,
    questions: [
      {
        id: 'reason',
        prompt: 'What brings you in today?',
        options: [
          { label: 'Tooth pain / swelling', value: 'pain', score: 35, urgency: true },
          { label: 'Broken tooth / filling', value: 'break', score: 30, urgency: true },
          { label: 'New patient checkup', value: 'new', score: 25 },
          { label: 'Whitening / cosmetic', value: 'cosmetic', score: 15 },
        ],
      },
      {
        id: 'patient',
        prompt: 'Are you an existing patient with us?',
        options: [
          { label: 'Yes, existing patient', value: 'existing', score: 20 },
          { label: 'No, new patient', value: 'new', score: 25 },
          { label: 'Not sure', value: 'unsure', score: 10 },
        ],
      },
      {
        id: 'timing',
        prompt: 'When would you prefer to come in?',
        options: [
          { label: 'First available tomorrow', value: 'asap', score: 25 },
          { label: 'Morning this week', value: 'morning', score: 15 },
          { label: 'Afternoon this week', value: 'afternoon', score: 15 },
          { label: 'Flexible', value: 'flex', score: 10 },
        ],
      },
    ],
    outcomes: {
      qualified: 'Lead qualified — appointment held for next working day.',
      triage: 'Urgent dental pain flagged — priority slot offered for tomorrow morning.',
      callback: 'Soft lead captured — practice notified for a warm callback.',
    },
  },
  {
    id: 'plumber',
    name: 'Plumbers',
    shortName: 'Plumbing',
    headline: 'A burst pipe after five still becomes a booked job.',
    summary:
      'Deskline answers every ring, grades urgency, captures address and access notes, then books the next available engineer window.',
    heroLine: 'For trade businesses that cannot afford a silent phone after hours.',
    image:
      'https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=1800&q=80',
    imageAlt: 'Plumber working on residential pipes',
    greeting:
      'You’ve reached Harbor Plumbing after hours. I’m Deskline — I can take job details now and book the next available engineer visit.',
    services: [
      'Leak / burst pipe',
      'Blocked drain',
      'Boiler / no hot water',
      'Toilet / cistern fault',
      'General repair quote',
    ],
    workingHours: { start: 8, end: 17, label: 'Mon–Sat · 8:00–17:00' },
    slotMinutes: 60,
    questions: [
      {
        id: 'issue',
        prompt: 'What’s going on at the property?',
        options: [
          { label: 'Active leak / flooding', value: 'flood', score: 40, urgency: true },
          { label: 'No hot water / boiler', value: 'boiler', score: 30, urgency: true },
          { label: 'Blocked drain / toilet', value: 'block', score: 25 },
          { label: 'Quote for a repair', value: 'quote', score: 15 },
        ],
      },
      {
        id: 'access',
        prompt: 'Can someone be on site during working hours tomorrow?',
        options: [
          { label: 'Yes, all day', value: 'all', score: 25 },
          { label: 'Morning only', value: 'am', score: 20 },
          { label: 'Afternoon only', value: 'pm', score: 20 },
          { label: 'Need to arrange access', value: 'later', score: 5 },
        ],
      },
      {
        id: 'postcode',
        prompt: 'Are you inside our usual service area?',
        options: [
          { label: 'Yes — local postcode', value: 'local', score: 25 },
          { label: 'Nearby / edge of area', value: 'edge', score: 15 },
          { label: 'Not sure', value: 'unsure', score: 10 },
          { label: 'Outside area', value: 'out', score: 0 },
        ],
      },
    ],
    outcomes: {
      qualified: 'Job qualified — engineer slot reserved for next working window.',
      triage: 'Emergency leak flagged — first available morning dispatch offered.',
      callback: 'Details logged — dispatcher notified for follow-up.',
    },
  },
  {
    id: 'medspa',
    name: 'Med spas',
    shortName: 'Med spa',
    headline: 'Curiosity after closing should still become a consult.',
    summary:
      'Deskline answers treatment enquiries, qualifies budget and readiness, then books consults into your next open calendar.',
    heroLine: 'For clinics that turn evening interest into booked consults.',
    image:
      'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=1800&q=80',
    imageAlt: 'Calm med spa treatment suite',
    greeting:
      'Thank you for calling Lumen Med Spa. Our studio is closed, but I’m Deskline — I can answer a few questions and reserve a consult for you.',
    services: [
      'Botox / toxin consult',
      'Dermal filler consult',
      'Laser / skin rejuvenation',
      'Hydrafacial / facial',
      'Membership enquiry',
    ],
    workingHours: { start: 10, end: 18, label: 'Tue–Sat · 10:00–18:00' },
    slotMinutes: 45,
    questions: [
      {
        id: 'interest',
        prompt: 'Which treatment are you curious about?',
        options: [
          { label: 'Injectables (Botox / filler)', value: 'inject', score: 30 },
          { label: 'Laser / skin', value: 'laser', score: 25 },
          { label: 'Facial / Hydrafacial', value: 'facial', score: 20 },
          { label: 'Not sure — want guidance', value: 'guide', score: 15 },
        ],
      },
      {
        id: 'timeline',
        prompt: 'How soon are you hoping to book?',
        options: [
          { label: 'This week if possible', value: 'week', score: 25 },
          { label: 'In the next 2–3 weeks', value: 'soon', score: 20 },
          { label: 'Just researching', value: 'research', score: 5 },
          { label: 'Event coming up', value: 'event', score: 30, urgency: true },
        ],
      },
      {
        id: 'consult',
        prompt: 'Would you like a consult reserved for our next open day?',
        options: [
          { label: 'Yes — first available', value: 'first', score: 25 },
          { label: 'Prefer a specific time', value: 'specific', score: 20 },
          { label: 'Send me options by text', value: 'sms', score: 10 },
          { label: 'Not yet', value: 'no', score: 0 },
        ],
      },
    ],
    outcomes: {
      qualified: 'Consult qualified — hold placed on next open clinic day.',
      triage: 'Time-sensitive event lead — priority consult offered.',
      callback: 'Interest captured — concierge team notified.',
    },
  },
]

export function getIndustry(id: IndustryId): Industry {
  return industries.find((item) => item.id === id) ?? industries[0]
}
