export type Plan = {
  id: string
  name: string
  price: number
  blurb: string
  bestFor: string
  features: string[]
  highlighted?: boolean
}

export const plans: Plan[] = [
  {
    id: 'frontline',
    name: 'Frontline',
    price: 1000,
    blurb: 'One location. Every missed call answered, qualified, and booked.',
    bestFor: 'Single-site dental, plumbing, or med spa teams',
    features: [
      'Unlimited after-hours call answering',
      'Industry script for one vertical',
      'Lead scoring + SMS confirmation',
      'Next-day working-hours booking',
      'Daily digest to your inbox',
      'Calendar sync (Google / Outlook)',
    ],
  },
  {
    id: 'practice',
    name: 'Practice',
    price: 1800,
    blurb: 'Deeper qualification, live handoff rules, and tighter diary control.',
    bestFor: 'Growing practices with two lines or busy evenings',
    highlighted: true,
    features: [
      'Everything in Frontline',
      'Custom qualification questions',
      'Priority / emergency triage rules',
      'Two numbers or locations',
      'CRM webhook + CSV export',
      'Weekly performance review',
    ],
  },
  {
    id: 'network',
    name: 'Network',
    price: 3000,
    blurb: 'Multi-site coverage with branded voice and dedicated success support.',
    bestFor: 'Groups, franchise sites, and high-volume call centers',
    features: [
      'Everything in Practice',
      'Up to five locations',
      'Custom voice + brand language',
      'Shared availability across sites',
      'Slack / Teams alerts',
      'Dedicated success manager',
    ],
  },
]
