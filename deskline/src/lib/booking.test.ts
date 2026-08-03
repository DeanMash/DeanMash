import { describe, expect, it } from 'vitest'
import { getIndustry } from '../data/industries'
import { buildSlots, nextWorkingDay, qualifyLead } from './booking'

describe('nextWorkingDay', () => {
  it('moves dental bookings to Monday after a Friday close', () => {
    // Friday 18:00 local
    const fridayEvening = new Date(2026, 7, 7, 18, 0, 0)
    const dental = getIndustry('dental')
    const day = nextWorkingDay(fridayEvening, dental)
    expect(day.getDay()).toBe(1)
    expect(day.getDate()).toBe(10)
  })

  it('keeps plumber bookings available on Saturday', () => {
    const fridayEvening = new Date(2026, 7, 7, 18, 0, 0)
    const plumber = getIndustry('plumber')
    const day = nextWorkingDay(fridayEvening, plumber)
    expect(day.getDay()).toBe(6)
  })
})

describe('qualifyLead', () => {
  it('triages urgent dental pain onto the first slot', () => {
    const dental = getIndustry('dental')
    const result = qualifyLead(
      dental,
      { reason: 'pain', patient: 'new', timing: 'asap' },
      new Date(2026, 7, 3, 19, 0, 0),
    )
    expect(result.status).toBe('triage')
    expect(result.urgent).toBe(true)
    expect(result.recommendedSlot).not.toBeNull()
  })

  it('returns callback for low-intent med spa research', () => {
    const medspa = getIndustry('medspa')
    const result = qualifyLead(medspa, {
      interest: 'guide',
      timeline: 'research',
      consult: 'no',
    })
    expect(result.status).toBe('callback')
    expect(result.recommendedSlot).toBeNull()
  })
})

describe('buildSlots', () => {
  it('returns slots inside working hours', () => {
    const dental = getIndustry('dental')
    const slots = buildSlots(dental, new Date(2026, 7, 3, 20, 0, 0), 4)
    expect(slots.length).toBe(4)
    for (const slot of slots) {
      expect(slot.start.getHours()).toBeGreaterThanOrEqual(9)
      expect(slot.start.getHours()).toBeLessThan(17)
    }
  })
})
