import type { PlanId } from "./types";

export interface Plan {
  id: PlanId;
  name: string;
  priceUsd: number;
  currencyLabel: string;
  tagline: string;
  locations: string;
  features: string[];
  bestFor: string;
  highlighted?: boolean;
}

/** Launch plan for small Zimbabwe shops — EcoCash $3 / month via Mashtech. */
export const ECOCASH_PLAN: Plan = {
  id: "ecocash_starter",
  name: "EcoCash Starter",
  priceUsd: 3,
  currencyLabel: "USD via EcoCash",
  tagline: "Register, get your link + QR, Mashtech posts happy reviews.",
  locations: "1 location",
  bestFor: "Restaurants, salons, workshops, pharmacies, lodges",
  highlighted: true,
  features: [
    "Company registration with unique review link + QR code",
    "Customers scan QR → your GladGate review page",
    "Automatic checks & WhatsApp/SMS follow-ups",
    "Happy reviews posted by Mashtech tagging your page",
    "Bad reviews held private for owner recovery",
    "$3 / month on EcoCash",
  ],
};

/** Kept for enterprise upsell demos; launch default is EcoCash Starter. */
export const PLANS: Plan[] = [
  ECOCASH_PLAN,
  {
    id: "neighborhood",
    name: "Neighborhood+",
    priceUsd: 15,
    currencyLabel: "USD",
    tagline: "Busier shops that need SMS fallback and weekly digests.",
    locations: "1 location",
    bestFor: "High-volume cafés and busy workshops",
    features: [
      "Everything in EcoCash Starter",
      "SMS fallback when WhatsApp fails",
      "Weekly reputation digest",
      "Priority Mashtech posting window",
    ],
  },
  {
    id: "street",
    name: "Multi-shop",
    priceUsd: 35,
    currencyLabel: "USD",
    tagline: "Up to 3 locations under one Mashtech account.",
    locations: "Up to 3 locations",
    bestFor: "Salon chains and multi-bay auto shops",
    features: [
      "Everything in Neighborhood+",
      "Multi-location dashboard",
      "Staff ask completion tracking",
      "Recovery playbooks",
    ],
  },
];

export function getPlan(id: PlanId): Plan {
  const found = PLANS.find((p) => p.id === id);
  if (!found) throw new Error(`Unknown plan: ${id}`);
  return found;
}

export const ECOCASH_MERCHANT = {
  name: "Mashtech GladGate",
  shortCodeHint: "Pay $3 to Mashtech GladGate on EcoCash",
  amountUsd: 3,
};
