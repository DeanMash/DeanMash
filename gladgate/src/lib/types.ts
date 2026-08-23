export type VerticalId =
  | "restaurant"
  | "auto_repair"
  | "salon"
  | "pharmacy"
  | "lodge"
  | "hardware"
  | "clinic"
  | "car_wash";

export type Channel = "whatsapp" | "sms";

export type PulseRating = 1 | 2 | 3 | 4 | 5;

export type ReviewDisposition =
  | "routed_public"
  | "held_private"
  | "awaiting_pulse";

export type FlagReason =
  | "low_score"
  | "complaint_language"
  | "refund_threat"
  | "safety_concern";

export type PlanId = "ecocash_starter" | "neighborhood" | "street" | "citywide";

export type SubscriptionStatus =
  | "trial"
  | "active"
  | "past_due"
  | "cancelled";

export type PaymentMethod = "ecocash" | "trial";

export interface Business {
  id: string;
  slug: string;
  name: string;
  vertical: VerticalId;
  city: string;
  country: string;
  ownerName: string;
  ownerPhone: string;
  whatsappNumber: string;
  facebookHandle: string;
  publicReviewUrl: string;
  planId: PlanId;
  subscriptionStatus: SubscriptionStatus;
  trialCode?: string;
  trialEndsAt?: string;
  nextBillingAt?: string;
  ecocashNumber?: string;
  reviewPath: string;
  dashboardPath: string;
  createdAt: string;
}

export interface RegisteredCustomer {
  id: string;
  businessId: string;
  name: string;
  phone: string;
  channel: Channel;
  lastServiceNote: string;
  registeredAt: string;
  lastContactAt?: string;
  nextFollowUpAt: string;
  followUpCount: number;
  optedOut: boolean;
}

export interface CustomerPulse {
  id: string;
  businessId: string;
  customerId?: string;
  customerName: string;
  phone: string;
  channel: Channel;
  serviceNote: string;
  createdAt: string;
  rating?: PulseRating;
  comment?: string;
  disposition: ReviewDisposition;
  flags: FlagReason[];
  publicReady: boolean;
}

export interface FlaggedReview {
  id: string;
  pulseId: string;
  businessId: string;
  customerName: string;
  rating: PulseRating;
  comment: string;
  flags: FlagReason[];
  status: "open" | "recovering" | "resolved";
  createdAt: string;
}

export interface SocialPost {
  id: string;
  businessId: string;
  pulseId: string;
  platform: "facebook" | "whatsapp_status";
  body: string;
  tagHandle: string;
  status: "queued" | "posted" | "failed";
  createdAt: string;
  postedAt?: string;
}

export interface FollowUpJob {
  id: string;
  businessId: string;
  customerId: string;
  customerName: string;
  phone: string;
  channel: Channel;
  dueAt: string;
  status: "due" | "sent" | "skipped";
  pulseId?: string;
}

export interface AskBatchResult {
  sent: number;
  channel: Channel;
  pulses: CustomerPulse[];
}

export interface TrialOffer {
  code: string;
  label: string;
  days: number;
  description: string;
  registerPath: string;
}
