import type { Business } from "./types";

/** One free trial for every new shop (days). Trial codes may extend this once at signup. */
export const DEFAULT_FREE_TRIAL_DAYS = 14;

export const ECOCASH_MONTHLY_USD = 3;

export const ECOCASH_MERCHANT = {
  name: "Mashtech GladGate",
  /** Shown on EcoCash pay screen */
  merchantCode: "GLADGATE",
  instruction: "Pay $3 USD on EcoCash to Mashtech GladGate. Use your payment reference.",
};

export function generatePaymentReference(slug: string): string {
  const suffix = Math.random().toString(36).slice(2, 8).toUpperCase();
  return `GG-${slug.slice(0, 12).toUpperCase()}-${suffix}`;
}

export function nextBillingDate(from = new Date()): string {
  const bill = new Date(from);
  bill.setMonth(bill.getMonth() + 1);
  return bill.toISOString();
}

export function isTrialActive(business: Business, now = new Date()): boolean {
  if (business.subscriptionStatus !== "trial") return false;
  if (!business.trialEndsAt) return false;
  return new Date(business.trialEndsAt).getTime() > now.getTime();
}

export function isSubscriptionActive(business: Business, now = new Date()): boolean {
  if (business.subscriptionStatus === "active") {
    if (!business.nextBillingAt) return true;
    return new Date(business.nextBillingAt).getTime() > now.getTime();
  }
  return isTrialActive(business, now);
}

export function syncSubscriptionStatus(business: Business, now = new Date()): Business {
  if (business.subscriptionStatus === "active") {
    if (business.nextBillingAt && new Date(business.nextBillingAt) <= now) {
      business.subscriptionStatus = "past_due";
    }
    return business;
  }

  if (business.subscriptionStatus === "trial" && business.trialEndsAt) {
    if (new Date(business.trialEndsAt) <= now) {
      business.subscriptionStatus = "past_due";
    }
  }

  return business;
}

export function verifyWebhookSecret(provided: string | null): boolean {
  const expected =
    process.env.ECOCASH_WEBHOOK_SECRET || "mashtech-ecocash-demo-secret";
  return Boolean(provided && provided === expected);
}
