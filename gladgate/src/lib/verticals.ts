import type { VerticalId } from "./types";

export interface Vertical {
  id: VerticalId;
  name: string;
  blurb: string;
  askMoment: string;
  exampleBusiness: string;
}

export const VERTICALS: Vertical[] = [
  {
    id: "restaurant",
    name: "Restaurants & cafés",
    blurb: "After the bill, while the meal is still warm.",
    askMoment: "Right after payment or takeaway handover",
    exampleBusiness: "Amanzi Grill, Harare",
  },
  {
    id: "auto_repair",
    name: "Auto repair & panel beaters",
    blurb: "When keys go back and the engine sounds right.",
    askMoment: "At vehicle collection",
    exampleBusiness: "Mbare Fast Fit",
  },
  {
    id: "salon",
    name: "Salons & barbers",
    blurb: "While they still love the mirror.",
    askMoment: "After styling, before they leave the chair",
    exampleBusiness: "Bloom Hair Studio, Bulawayo",
  },
  {
    id: "pharmacy",
    name: "Pharmacies",
    blurb: "Quick pulse after counsel — not a public rant later.",
    askMoment: "After dispensing and advice",
    exampleBusiness: "Green Cross Pharmacy",
  },
  {
    id: "lodge",
    name: "Lodges & guesthouses",
    blurb: "Checkout ask, before TripAdvisor becomes a diary.",
    askMoment: "Morning of checkout",
    exampleBusiness: "Msasa Lodge, Victoria Falls",
  },
  {
    id: "hardware",
    name: "Hardware & spares",
    blurb: "Trade customers who got the right part, first time.",
    askMoment: "After counter sale or delivery",
    exampleBusiness: "Copperbelt Spares",
  },
  {
    id: "clinic",
    name: "Clinics & dental",
    blurb: "Private first — clinical trust never belongs on a wall of stars.",
    askMoment: "After consultation checkout",
    exampleBusiness: "Borrowdale Family Clinic",
  },
  {
    id: "car_wash",
    name: "Car washes",
    blurb: "When the paint is still wet-looking and pride is high.",
    askMoment: "At hand-over bay",
    exampleBusiness: "Shine Bay Avondale",
  },
];

export function getVertical(id: VerticalId): Vertical {
  const found = VERTICALS.find((v) => v.id === id);
  if (!found) throw new Error(`Unknown vertical: ${id}`);
  return found;
}
