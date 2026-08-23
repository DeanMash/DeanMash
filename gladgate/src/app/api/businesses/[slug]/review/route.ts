import { NextResponse } from "next/server";
import { createPublicReviewPulse } from "@/lib/store";
import { privatePrompt, publicPrompt } from "@/lib/engine";
import type { PulseRating } from "@/lib/types";

export async function POST(
  request: Request,
  context: { params: Promise<{ slug: string }> },
) {
  const { slug } = await context.params;
  const body = (await request.json()) as {
    customerName?: string;
    phone?: string;
    rating?: number;
    comment?: string;
  };

  if (!body.rating || body.rating < 1 || body.rating > 5) {
    return NextResponse.json(
      { error: "rating (1-5) is required" },
      { status: 400 },
    );
  }

  try {
    const result = createPublicReviewPulse({
      businessSlug: slug,
      customerName: body.customerName || "Guest",
      phone: body.phone,
      rating: body.rating as PulseRating,
      comment: body.comment,
    });

    const message =
      result.pulse.disposition === "routed_public"
        ? publicPrompt(result.businessName)
        : privatePrompt(result.businessName);

    return NextResponse.json({
      ...result,
      message,
      mashtechNote:
        result.pulse.disposition === "routed_public"
          ? "Mashtech queued a social post tagging this business page."
          : "Held private — Mashtech will not post this publicly.",
    });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed" },
      { status: 404 },
    );
  }
}
