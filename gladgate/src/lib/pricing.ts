import type { PlanId } from "./types";

export interface Plan {
  id: PlanId;
  name: string;
  priceUsd: number;
  tagline: string;
  locations: string;
  features: string[];
  bestFor: string;
}

export const PLANS: Plan[] = [
  {
    id: "neighborhood",
    name: "Neighborhood",
    priceUsd: 500,
    tagline: "One busy shop. Every happy walk-out asked.",
    locations: "1 location",
    bestFor: "Single restaurant, salon, or workshop",
    features: [
      "WhatsApp pulse asks after every visit",
      "Happy customers routed to Google / Facebook",
      "Unhappy feedback held private + owner SMS",
      "Complaint keyword flagging",
      "USD or EcoCash billing",
    ],
  },
  {
    id: "street",
    name: "Street Smart",
    priceUsd: 900,
    tagline: "Staff on shift. Reviews on rails.",
    locations: "Up to 3 locations",
    bestFor: "Growing auto shops, salon chains, popular cafés",
    features: [
      "Everything in Neighborhood",
      "SMS fallback when WhatsApp fails",
      "Staff performance on ask completion",
      "Weekly reputation digest (WhatsApp)",
      "Recovery playbooks for flagged visits",
      "Priority onboarding in Zimbabwe & region",
    ],
  },
  {
    id: "citywide",
    name: "Citywide",
    priceUsd: 1500,
    tagline: "Multi-site reputation, one control room.",
    locations: "Up to 10 locations",
    bestFor: "Lodge groups, pharmacy networks, multi-bay workshops",
    features: [
      "Everything in Street Smart",
      "Multi-location dashboard & manager alerts",
      "Custom public review destinations",
      "Monthly coaching call",
      "API / POS webhook triggers",
      "Brand protection review before anything goes public",
    ],
  },
];

export function getPlan(id: PlanId): Plan {
  const found = PLANS.find((p) => p.id === id);
  if (!found) throw new Error(`Unknown plan: ${id}`);
  return found;
}
