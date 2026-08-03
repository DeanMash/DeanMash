import { NextResponse } from "next/server";
import { getPulse, submitPulseResponse } from "@/lib/store";
import { privatePrompt, publicPrompt } from "@/lib/engine";
import type { PulseRating } from "@/lib/types";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const pulseId = searchParams.get("id");
  if (!pulseId) {
    return NextResponse.json({ error: "Missing id" }, { status: 400 });
  }
  const pulse = getPulse(pulseId);
  if (!pulse) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
  return NextResponse.json({ pulse });
}

export async function POST(request: Request) {
  const body = (await request.json()) as {
    pulseId?: string;
    rating?: number;
    comment?: string;
  };

  if (!body.pulseId || !body.rating || body.rating < 1 || body.rating > 5) {
    return NextResponse.json(
      { error: "pulseId and rating (1-5) are required" },
      { status: 400 },
    );
  }

  try {
    const result = submitPulseResponse({
      pulseId: body.pulseId,
      rating: body.rating as PulseRating,
      comment: body.comment,
    });

    const message =
      result.pulse.disposition === "routed_public"
        ? publicPrompt(result.businessName)
        : privatePrompt(result.businessName);

    return NextResponse.json({ ...result, message });
  } catch {
    return NextResponse.json({ error: "Pulse not found" }, { status: 404 });
  }
}
