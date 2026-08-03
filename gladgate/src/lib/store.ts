import { decideDisposition } from "./engine";
import type {
  AskBatchResult,
  Business,
  Channel,
  CustomerPulse,
  FlaggedReview,
  PulseRating,
} from "./types";

interface DemoState {
  business: Business;
  pulses: CustomerPulse[];
  flagged: FlaggedReview[];
  publicRouted: number;
  asksSent: number;
}

const DEMO_CUSTOMERS = [
  { name: "Tendai Moyo", phone: "+263771234501", note: "Lunch table 4 — sadza & oxtail" },
  { name: "Chipo Ncube", phone: "+263772345602", note: "Full colour + blowdry" },
  { name: "Farai Dube", phone: "+263773456703", note: "Brake pads + oil service" },
  { name: "Rudo Sibanda", phone: "+263774567804", note: "2-night lodge stay" },
  { name: "Tafadzwa Chirwa", phone: "+263775678905", note: "Prescription + BP check" },
  { name: "Blessing Phiri", phone: "+263776789006", note: "Exterior + interior wash" },
];

function defaultState(): DemoState {
  return {
    business: {
      id: "biz_amanzi",
      name: "Amanzi Grill",
      vertical: "restaurant",
      city: "Harare",
      country: "Zimbabwe",
      publicReviewUrl: "https://g.page/r/demo-amanzi-grill/review",
      whatsappNumber: "+263771000200",
      planId: "street",
    },
    pulses: [],
    flagged: [],
    publicRouted: 0,
    asksSent: 0,
  };
}

function getState(): DemoState {
  const g = globalThis as typeof globalThis & { __gladgate?: DemoState };
  if (!g.__gladgate) {
    g.__gladgate = defaultState();
  }
  return g.__gladgate;
}

function uid(prefix: string): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 9)}`;
}

export function getDemoSnapshot() {
  const state = getState();
  return {
    business: state.business,
    pulses: [...state.pulses].sort((a, b) =>
      b.createdAt.localeCompare(a.createdAt),
    ),
    flagged: [...state.flagged].sort((a, b) =>
      b.createdAt.localeCompare(a.createdAt),
    ),
    stats: {
      asksSent: state.asksSent,
      publicRouted: state.publicRouted,
      heldPrivate: state.flagged.filter((f) => f.status !== "resolved").length,
      happyRate:
        state.pulses.filter((p) => p.disposition === "routed_public").length &&
        state.pulses.filter((p) => p.rating).length
          ? Math.round(
              (state.pulses.filter((p) => p.disposition === "routed_public")
                .length /
                state.pulses.filter((p) => p.rating).length) *
                100,
            )
          : 0,
    },
  };
}

export function resetDemo(): ReturnType<typeof getDemoSnapshot> {
  const g = globalThis as typeof globalThis & { __gladgate?: DemoState };
  g.__gladgate = defaultState();
  return getDemoSnapshot();
}

export function sendAskBatch(
  count = 3,
  channel: Channel = "whatsapp",
): AskBatchResult {
  const state = getState();
  const pulses: CustomerPulse[] = [];
  const start = state.asksSent % DEMO_CUSTOMERS.length;

  for (let i = 0; i < count; i += 1) {
    const customer = DEMO_CUSTOMERS[(start + i) % DEMO_CUSTOMERS.length];
    const pulse: CustomerPulse = {
      id: uid("pulse"),
      businessId: state.business.id,
      customerName: customer.name,
      phone: customer.phone,
      channel,
      serviceNote: customer.note,
      createdAt: new Date().toISOString(),
      disposition: "awaiting_pulse",
      flags: [],
      publicReady: false,
    };
    state.pulses.unshift(pulse);
    pulses.push(pulse);
  }

  state.asksSent += count;
  return { sent: count, channel, pulses };
}

export function submitPulseResponse(input: {
  pulseId: string;
  rating: PulseRating;
  comment?: string;
}) {
  const state = getState();
  const pulse = state.pulses.find((p) => p.id === input.pulseId);
  if (!pulse) {
    throw new Error("Pulse not found");
  }

  const comment = input.comment?.trim() ?? "";
  const decision = decideDisposition(input.rating, comment);

  pulse.rating = input.rating;
  pulse.comment = comment;
  pulse.disposition = decision.disposition;
  pulse.flags = decision.flags;
  pulse.publicReady = decision.publicReady;

  let flagged: FlaggedReview | undefined;
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
    state.publicRouted += 1;
  }

  return {
    pulse,
    flagged,
    publicReviewUrl: decision.publicReady
      ? state.business.publicReviewUrl
      : null,
    businessName: state.business.name,
  };
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
