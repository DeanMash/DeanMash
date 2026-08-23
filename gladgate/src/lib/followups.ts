/** Follow-up cadence after a customer is registered (hours from registration / last contact). */
export const FOLLOW_UP_HOURS = [24, 24 * 7, 24 * 30] as const;

export function nextFollowUpAt(
  from: Date,
  followUpCount: number,
): string {
  const hours =
    FOLLOW_UP_HOURS[Math.min(followUpCount, FOLLOW_UP_HOURS.length - 1)];
  const due = new Date(from.getTime() + hours * 60 * 60 * 1000);
  return due.toISOString();
}

export function isDue(iso: string, now = new Date()): boolean {
  return new Date(iso).getTime() <= now.getTime();
}
