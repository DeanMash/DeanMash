import { decideDisposition } from "./engine";
import { nextFollowUpAt, isDue } from "./followups";
import { createQueuedPost, markPosted } from "./social";
import { findTrial, trialEndsAt } from "./trials";
import type {
  AskBatchResult,
  Business,
  Channel,
  CustomerPulse,
  FlaggedReview,
  FollowUpJob,
  PulseRating,
  RegisteredCustomer,
  SocialPost,
  VerticalId,
} from "./types";

interface AppState {
  businesses: Business[];
  customers: RegisteredCustomer[];
  pulses: CustomerPulse[];
  flagged: FlaggedReview[];
  socialPosts: SocialPost[];
}

function uid(prefix: string): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 9)}`;
}

function slugify(name: string): string {
  const base = name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 40);
  return base || `shop-${uid("s").slice(-5)}`;
}

function uniqueSlug(state: AppState, name: string): string {
  let slug = slugify(name);
  let n = 2;
  while (state.businesses.some((b) => b.slug === slug)) {
    slug = `${slugify(name)}-${n}`;
    n += 1;
  }
  return slug;
}

function seedBusiness(): Business {
  const slug = "amanzi-grill";
  return {
    id: "biz_amanzi",
    slug,
    name: "Amanzi Grill",
    vertical: "restaurant",
    city: "Harare",
    country: "Zimbabwe",
    ownerName: "Tariro Mash",
    ownerPhone: "+263771000200",
    whatsappNumber: "+263771000200",
    facebookHandle: "@AmanziGrillHre",
    publicReviewUrl: "https://g.page/r/demo-amanzi-grill/review",
    planId: "ecocash_starter",
    subscriptionStatus: "trial",
    trialCode: "MASHTECH14",
    trialEndsAt: trialEndsAt(14),
    reviewPath: `/b/${slug}`,
    dashboardPath: `/b/${slug}/dashboard`,
    createdAt: new Date().toISOString(),
  };
}

function defaultState(): AppState {
  return {
    businesses: [seedBusiness()],
    customers: [],
    pulses: [],
    flagged: [],
    socialPosts: [],
  };
}

function getState(): AppState {
  const g = globalThis as typeof globalThis & { __gladgate_v2?: AppState };
  if (!g.__gladgate_v2) {
    g.__gladgate_v2 = defaultState();
  }
  return g.__gladgate_v2;
}

export function resetStore(): void {
  const g = globalThis as typeof globalThis & { __gladgate_v2?: AppState };
  g.__gladgate_v2 = defaultState();
}

export function listBusinesses(): Business[] {
  return [...getState().businesses].sort((a, b) =>
    b.createdAt.localeCompare(a.createdAt),
  );
}

export function getBusinessBySlug(slug: string): Business | undefined {
  return getState().businesses.find((b) => b.slug === slug);
}

export function getBusinessById(id: string): Business | undefined {
  return getState().businesses.find((b) => b.id === id);
}

export type RegisterInput = {
  name: string;
  vertical: VerticalId;
  city: string;
  country?: string;
  ownerName: string;
  ownerPhone: string;
  whatsappNumber?: string;
  facebookHandle: string;
  trialCode?: string;
  ecocashNumber?: string;
  payNow?: boolean;
};

export function registerBusiness(input: RegisterInput): {
  business: Business;
  trialApplied: boolean;
  message: string;
} {
  const state = getState();
  const name = input.name.trim();
  if (!name) throw new Error("Business name is required");
  if (!input.ownerPhone.trim()) throw new Error("Owner phone is required");
  if (!input.facebookHandle.trim()) {
    throw new Error("Facebook / social handle is required for Mashtech tagging");
  }

  const trial = input.trialCode ? findTrial(input.trialCode) : undefined;
  if (input.trialCode && !trial) {
    throw new Error("Invalid trial code");
  }

  const slug = uniqueSlug(state, name);
  const now = new Date();
  let subscriptionStatus: Business["subscriptionStatus"] = "trial";
  let trialEnds: string | undefined;
  let nextBillingAt: string | undefined;
  let message: string;

  if (trial) {
    trialEnds = trialEndsAt(trial.days, now);
    subscriptionStatus = "trial";
    message = `Trial ${trial.code} applied for ${trial.days} days. Your link and QR are ready.`;
  } else if (input.payNow && input.ecocashNumber) {
    subscriptionStatus = "active";
    const bill = new Date(now);
    bill.setMonth(bill.getMonth() + 1);
    nextBillingAt = bill.toISOString();
    message =
      "EcoCash $3 payment recorded (demo). Mashtech will renew monthly.";
  } else {
    // Soft trial for launch so shops can still get a link before paying
    trialEnds = trialEndsAt(7, now);
    subscriptionStatus = "trial";
    message =
      "7-day soft trial started. Use a trial code or EcoCash $3 to continue after launch.";
  }

  const business: Business = {
    id: uid("biz"),
    slug,
    name,
    vertical: input.vertical,
    city: input.city.trim() || "Harare",
    country: input.country?.trim() || "Zimbabwe",
    ownerName: input.ownerName.trim() || "Owner",
    ownerPhone: input.ownerPhone.trim(),
    whatsappNumber: (input.whatsappNumber || input.ownerPhone).trim(),
    facebookHandle: input.facebookHandle.trim().replace(/^@/, "@"),
    publicReviewUrl: "",
    planId: "ecocash_starter",
    subscriptionStatus,
    trialCode: trial?.code,
    trialEndsAt: trialEnds,
    nextBillingAt,
    ecocashNumber: input.ecocashNumber?.trim(),
    reviewPath: `/b/${slug}`,
    dashboardPath: `/b/${slug}/dashboard`,
    createdAt: now.toISOString(),
  };

  // Ensure facebook handle has @
  if (!business.facebookHandle.startsWith("@")) {
    business.facebookHandle = `@${business.facebookHandle}`;
  }

  state.businesses.unshift(business);
  return { business, trialApplied: Boolean(trial), message };
}

export function getBusinessSnapshot(slug: string) {
  const business = getBusinessBySlug(slug);
  if (!business) return null;
  const state = getState();
  const pulses = state.pulses
    .filter((p) => p.businessId === business.id)
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  const flagged = state.flagged
    .filter((f) => f.businessId === business.id)
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  const customers = state.customers
    .filter((c) => c.businessId === business.id)
    .sort((a, b) => b.registeredAt.localeCompare(a.registeredAt));
  const socialPosts = state.socialPosts
    .filter((s) => s.businessId === business.id)
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  const rated = pulses.filter((p) => p.rating);
  const publicRouted = pulses.filter((p) => p.disposition === "routed_public");

  return {
    business,
    pulses,
    flagged,
    customers,
    socialPosts,
    stats: {
      customers: customers.length,
      asksSent: pulses.length,
      publicRouted: publicRouted.length,
      heldPrivate: flagged.filter((f) => f.status !== "resolved").length,
      socialQueued: socialPosts.filter((s) => s.status === "queued").length,
      socialPosted: socialPosts.filter((s) => s.status === "posted").length,
      happyRate: rated.length
        ? Math.round((publicRouted.length / rated.length) * 100)
        : 0,
      followUpsDue: customers.filter(
        (c) => !c.optedOut && isDue(c.nextFollowUpAt),
      ).length,
    },
  };
}

/** Legacy demo helpers — operate on Amanzi Grill seed. */
export function getDemoSnapshot() {
  const snap = getBusinessSnapshot("amanzi-grill");
  if (!snap) throw new Error("Demo business missing");
  return snap;
}

export function resetDemo() {
  resetStore();
  return getDemoSnapshot();
}

export function registerCustomer(input: {
  businessSlug: string;
  name: string;
  phone: string;
  channel?: Channel;
  serviceNote?: string;
}): RegisteredCustomer {
  const business = getBusinessBySlug(input.businessSlug);
  if (!business) throw new Error("Business not found");
  const state = getState();
  const phone = input.phone.trim();
  const existing = state.customers.find(
    (c) => c.businessId === business.id && c.phone === phone,
  );
  if (existing) {
    existing.name = input.name.trim() || existing.name;
    existing.lastServiceNote =
      input.serviceNote?.trim() || existing.lastServiceNote;
    existing.lastContactAt = new Date().toISOString();
    return existing;
  }

  const now = new Date();
  const customer: RegisteredCustomer = {
    id: uid("cust"),
    businessId: business.id,
    name: input.name.trim() || "Customer",
    phone,
    channel: input.channel === "sms" ? "sms" : "whatsapp",
    lastServiceNote: input.serviceNote?.trim() || "Visit",
    registeredAt: now.toISOString(),
    // First automatic check is due immediately so shops can demo follow-ups;
    // later cadence uses FOLLOW_UP_HOURS (1 day → 7 days → 30 days).
    nextFollowUpAt: now.toISOString(),
    followUpCount: 0,
    optedOut: false,
  };
  state.customers.unshift(customer);
  return customer;
}

export function sendAskBatch(
  count = 3,
  channel: Channel = "whatsapp",
  businessSlug = "amanzi-grill",
): AskBatchResult {
  const business = getBusinessBySlug(businessSlug);
  if (!business) throw new Error("Business not found");
  const state = getState();
  const customers = state.customers.filter((c) => c.businessId === business.id);
  const pulses: CustomerPulse[] = [];

  const fallback = [
    { name: "Tendai Moyo", phone: "+263771234501", note: "Lunch — sadza & oxtail" },
    { name: "Chipo Ncube", phone: "+263772345602", note: "Full colour + blowdry" },
    { name: "Farai Dube", phone: "+263773456703", note: "Brake pads + oil service" },
  ];

  for (let i = 0; i < count; i += 1) {
    let name: string;
    let phone: string;
    let note: string;
    let customerId: string | undefined;

    if (customers.length > 0) {
      const c = customers[i % customers.length];
      name = c.name;
      phone = c.phone;
      note = c.lastServiceNote;
      customerId = c.id;
    } else {
      const f = fallback[i % fallback.length];
      name = f.name;
      phone = f.phone;
      note = f.note;
    }

    const pulse: CustomerPulse = {
      id: uid("pulse"),
      businessId: business.id,
      customerId,
      customerName: name,
      phone,
      channel,
      serviceNote: note,
      createdAt: new Date().toISOString(),
      disposition: "awaiting_pulse",
      flags: [],
      publicReady: false,
    };
    state.pulses.unshift(pulse);
    pulses.push(pulse);
  }

  return { sent: count, channel, pulses };
}

export function createPublicReviewPulse(input: {
  businessSlug: string;
  customerName: string;
  phone?: string;
  rating: PulseRating;
  comment?: string;
}) {
  const business = getBusinessBySlug(input.businessSlug);
  if (!business) throw new Error("Business not found");
  const state = getState();

  const pulse: CustomerPulse = {
    id: uid("pulse"),
    businessId: business.id,
    customerName: input.customerName.trim() || "Guest",
    phone: input.phone?.trim() || "",
    channel: "whatsapp",
    serviceNote: "QR / review link visit",
    createdAt: new Date().toISOString(),
    disposition: "awaiting_pulse",
    flags: [],
    publicReady: false,
  };
  state.pulses.unshift(pulse);

  if (input.phone?.trim()) {
    registerCustomer({
      businessSlug: input.businessSlug,
      name: pulse.customerName,
      phone: input.phone.trim(),
      serviceNote: "Left a review via QR / link",
    });
  }

  return submitPulseResponse({
    pulseId: pulse.id,
    rating: input.rating,
    comment: input.comment,
  });
}

export function submitPulseResponse(input: {
  pulseId: string;
  rating: PulseRating;
  comment?: string;
}) {
  const state = getState();
  const pulse = state.pulses.find((p) => p.id === input.pulseId);
  if (!pulse) throw new Error("Pulse not found");
  const business = getBusinessById(pulse.businessId);
  if (!business) throw new Error("Business not found");

  const comment = input.comment?.trim() ?? "";
  const decision = decideDisposition(input.rating, comment);

  pulse.rating = input.rating;
  pulse.comment = comment;
  pulse.disposition = decision.disposition;
  pulse.flags = decision.flags;
  pulse.publicReady = decision.publicReady;

  let flagged: FlaggedReview | undefined;
  let social: SocialPost | undefined;

  if (decision.disposition === "held_private") {
    flagged = {
      id: uid("flag"),
      pulseId: pulse.id,
      businessId: pulse.businessId,
      customerName: pulse.customerName,
      rating: input.rating,
      comment,
      flags: decision.flags,
      status: "open",
      createdAt: new Date().toISOString(),
    };
    state.flagged.unshift(flagged);
  } else {
    social = createQueuedPost(business, pulse);
    state.socialPosts.unshift(social);
  }

  if (pulse.customerId) {
    const customer = state.customers.find((c) => c.id === pulse.customerId);
    if (customer) {
      customer.lastContactAt = new Date().toISOString();
      customer.followUpCount += 1;
      customer.nextFollowUpAt = nextFollowUpAt(
        new Date(),
        customer.followUpCount,
      );
    }
  }

  return {
    pulse,
    flagged,
    social,
    publicReviewUrl: decision.publicReady ? business.reviewPath : null,
    businessName: business.name,
    mashtechTagged: Boolean(social),
  };
}

export function publishSocialQueue(businessSlug: string) {
  const business = getBusinessBySlug(businessSlug);
  if (!business) throw new Error("Business not found");
  const state = getState();
  const posted: SocialPost[] = [];
  for (const post of state.socialPosts) {
    if (post.businessId === business.id && post.status === "queued") {
      Object.assign(post, markPosted(post));
      posted.push(post);
    }
  }
  return { posted: posted.length, posts: posted };
}

export function updateFlagStatus(
  flagId: string,
  status: FlaggedReview["status"],
) {
  const state = getState();
  const flag = state.flagged.find((f) => f.id === flagId);
  if (!flag) throw new Error("Flag not found");
  flag.status = status;
  return flag;
}

export function getPulse(pulseId: string) {
  return getState().pulses.find((p) => p.id === pulseId);
}

export function runDueFollowUps(businessSlug: string): {
  jobs: FollowUpJob[];
  pulses: CustomerPulse[];
} {
  const business = getBusinessBySlug(businessSlug);
  if (!business) throw new Error("Business not found");
  const state = getState();
  const dueCustomers = state.customers.filter(
    (c) =>
      c.businessId === business.id && !c.optedOut && isDue(c.nextFollowUpAt),
  );

  const pulses: CustomerPulse[] = [];
  const jobs: FollowUpJob[] = [];

  for (const customer of dueCustomers) {
    const pulse: CustomerPulse = {
      id: uid("pulse"),
      businessId: business.id,
      customerId: customer.id,
      customerName: customer.name,
      phone: customer.phone,
      channel: customer.channel,
      serviceNote: `Automatic follow-up #${customer.followUpCount + 1}`,
      createdAt: new Date().toISOString(),
      disposition: "awaiting_pulse",
      flags: [],
      publicReady: false,
    };
    state.pulses.unshift(pulse);
    pulses.push(pulse);

    jobs.push({
      id: uid("job"),
      businessId: business.id,
      customerId: customer.id,
      customerName: customer.name,
      phone: customer.phone,
      channel: customer.channel,
      dueAt: customer.nextFollowUpAt,
      status: "sent",
      pulseId: pulse.id,
    });

    customer.lastContactAt = new Date().toISOString();
    customer.followUpCount += 1;
    customer.nextFollowUpAt = nextFollowUpAt(
      new Date(),
      customer.followUpCount,
    );
  }

  return { jobs, pulses };
}

export function activateEcoCash(input: {
  businessSlug: string;
  ecocashNumber: string;
}) {
  const business = getBusinessBySlug(input.businessSlug);
  if (!business) throw new Error("Business not found");
  if (!input.ecocashNumber.trim()) throw new Error("EcoCash number required");

  business.subscriptionStatus = "active";
  business.ecocashNumber = input.ecocashNumber.trim();
  business.planId = "ecocash_starter";
  const bill = new Date();
  bill.setMonth(bill.getMonth() + 1);
  business.nextBillingAt = bill.toISOString();
  business.trialEndsAt = undefined;
  return business;
}
