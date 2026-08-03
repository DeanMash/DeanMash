import type { FlagReason, PulseRating, ReviewDisposition } from "./types";

const COMPLAINT_PATTERNS: { reason: FlagReason; pattern: RegExp }[] = [
  {
    reason: "complaint_language",
    pattern:
      /\b(worst|terrible|awful|disgusting|rude|scam|never again|waste|horrible|pathetic)\b/i,
  },
  {
    reason: "refund_threat",
    pattern: /\b(refund|chargeback|lawyer|sue|police|report you|consumer council)\b/i,
  },
  {
    reason: "safety_concern",
    pattern:
      /\b(food\s*poison\w*|sick|allerg\w*|unsafe|injur\w*|bleed\w*|infection|stolen|theft)\b/i,
  },
];

export function scoreIsHappy(rating: PulseRating): boolean {
  return rating >= 4;
}

export function detectFlags(
  rating: PulseRating,
  comment: string,
): FlagReason[] {
  const flags = new Set<FlagReason>();

  if (rating <= 3) {
    flags.add("low_score");
  }

  const text = comment.trim();
  if (text) {
    for (const { reason, pattern } of COMPLAINT_PATTERNS) {
      if (pattern.test(text)) {
        flags.add(reason);
      }
    }
  }

  return [...flags];
}

export function decideDisposition(
  rating: PulseRating,
  comment: string,
): { disposition: ReviewDisposition; flags: FlagReason[]; publicReady: boolean } {
  const flags = detectFlags(rating, comment);
  const happy = scoreIsHappy(rating) && flags.length === 0;

  if (happy) {
    return {
      disposition: "routed_public",
      flags: [],
      publicReady: true,
    };
  }

  // Even a 5-star with complaint language stays private until reviewed.
  return {
    disposition: "held_private",
    flags: flags.length ? flags : ["low_score"],
    publicReady: false,
  };
}

export function publicPrompt(businessName: string): string {
  return `Thank you — we are glad it went well. A short public review for ${businessName} helps neighbours find us. Tap below when you have 30 seconds.`;
}

export function privatePrompt(businessName: string): string {
  return `Thank you for telling ${businessName} privately. Your note will not be posted publicly. An owner will follow up to make this right.`;
}
