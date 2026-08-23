import type { TrialOffer } from "./types";

/** Pre-launch trial codes — share these before public EcoCash billing goes live. */
export const TRIAL_OFFERS: TrialOffer[] = [
  {
    code: "MASHTECH14",
    label: "Mashtech 14-day trial",
    days: 14,
    description: "Full GladGate for 14 days — link, QR, follow-ups, social posting.",
    registerPath: "/register?code=MASHTECH14",
  },
  {
    code: "GLADLAUNCH",
    label: "Launch month",
    days: 30,
    description: "30-day free trial for early Zimbabwe partners.",
    registerPath: "/register?code=GLADLAUNCH",
  },
  {
    code: "ECOCASH3",
    label: "Extended free trial",
    days: 30,
    description:
      "One free trial for 30 days, then $3 / month on EcoCash after Mashtech confirms payment.",
    registerPath: "/register?code=ECOCASH3",
  },
  {
    code: "DEMOQR",
    label: "QR desk demo",
    days: 7,
    description: "One-week trial for printing a counter QR and testing reviews.",
    registerPath: "/register?code=DEMOQR",
  },
];

export function findTrial(code: string): TrialOffer | undefined {
  const normalized = code.trim().toUpperCase();
  return TRIAL_OFFERS.find((t) => t.code === normalized);
}

export function trialEndsAt(days: number, from = new Date()): string {
  const end = new Date(from);
  end.setDate(end.getDate() + days);
  return end.toISOString();
}
