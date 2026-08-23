import type { Business, CustomerPulse, SocialPost } from "./types";

function uid(prefix: string): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 9)}`;
}

function handleOf(business: Business): string {
  return business.facebookHandle.startsWith("@")
    ? business.facebookHandle
    : `@${business.facebookHandle}`;
}

/** Auto-created when a shop registers — Mashtech uses this to announce the project. */
export function buildLaunchPost(
  business: Business,
): Omit<SocialPost, "id" | "createdAt" | "status"> {
  const handle = handleOf(business);
  const readyCaption = `Now on GladGate ✨

${business.name} (${business.city}) is collecting reviews with a counter QR — happy voices go public, problems stay private.

Tagging ${handle}
Powered by Mashtech · Scan their QR or ask staff for the review link.`;

  return {
    businessId: business.id,
    pulseId: "launch",
    kind: "launch",
    platform: "facebook",
    body: readyCaption,
    readyCaption,
    tagHandle: handle,
  };
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
  const handle = handleOf(business);

  const readyCaption = `${stars} ${pulse.customerName} loved ${business.name}${quote}

Posted by Mashtech GladGate · tagging ${handle}
Scan their counter QR to leave yours.`;

  return {
    businessId: business.id,
    pulseId: pulse.id,
    kind: "review",
    platform: "facebook",
    body: readyCaption,
    readyCaption,
    tagHandle: handle,
  };
}

export function createLaunchPost(business: Business): SocialPost {
  const draft = buildLaunchPost(business);
  return {
    id: uid("social"),
    ...draft,
    status: "queued",
    createdAt: new Date().toISOString(),
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
