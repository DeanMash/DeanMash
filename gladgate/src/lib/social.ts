import type { Business, CustomerPulse, SocialPost } from "./types";

function uid(prefix: string): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 9)}`;
}

/** Mashtech posts happy reviews and tags the business social page. */
export function buildMashtechPost(
  business: Business,
  pulse: CustomerPulse,
): Omit<SocialPost, "id" | "createdAt" | "status"> {
  const stars = "★".repeat(pulse.rating ?? 5);
  const quote = pulse.comment?.trim()
    ? ` — “${pulse.comment.trim()}”`
    : "";
  const handle = business.facebookHandle.startsWith("@")
    ? business.facebookHandle
    : `@${business.facebookHandle}`;

  const body = `${stars} ${pulse.customerName} loved ${business.name}${quote}

Posted automatically by Mashtech GladGate, tagging ${handle}.
Scan their counter QR or open their review link to leave yours.`;

  return {
    businessId: business.id,
    pulseId: pulse.id,
    platform: "facebook",
    body,
    tagHandle: handle,
  };
}

export function createQueuedPost(
  business: Business,
  pulse: CustomerPulse,
): SocialPost {
  const draft = buildMashtechPost(business, pulse);
  return {
    id: uid("social"),
    ...draft,
    status: "queued",
    createdAt: new Date().toISOString(),
  };
}

export function markPosted(post: SocialPost): SocialPost {
  return {
    ...post,
    status: "posted",
    postedAt: new Date().toISOString(),
  };
}
