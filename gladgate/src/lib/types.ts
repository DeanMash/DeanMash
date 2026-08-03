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

export interface Business {
  id: string;
  name: string;
  vertical: VerticalId;
  city: string;
  country: string;
  publicReviewUrl: string;
  whatsappNumber: string;
  planId: PlanId;
}

export type PlanId = "neighborhood" | "street" | "citywide";

export interface CustomerPulse {
  id: string;
  businessId: string;
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

export interface AskBatchResult {
  sent: number;
  channel: Channel;
  pulses: CustomerPulse[];
}
