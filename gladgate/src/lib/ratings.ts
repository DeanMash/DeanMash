import type { CustomerPulse, PulseRating } from "./types";

export interface RatingSummary {
  average: number | null;
  count: number;
  starsLabel: string;
}

export function averageRating(
  pulses: Pick<CustomerPulse, "rating">[],
): RatingSummary {
  const rated = pulses.filter(
    (p): p is { rating: PulseRating } =>
      p.rating !== undefined && p.rating >= 1 && p.rating <= 5,
  );
  if (!rated.length) {
    return { average: null, count: 0, starsLabel: "No ratings yet" };
  }
  const sum = rated.reduce((acc, p) => acc + p.rating, 0);
  const average = Math.round((sum / rated.length) * 10) / 10;
  return {
    average,
    count: rated.length,
    starsLabel: `${average} ★ (${rated.length} review${rated.length === 1 ? "" : "s"})`,
  };
}
