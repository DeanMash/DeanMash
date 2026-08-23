import { NextResponse } from "next/server";
import { registerCustomer, runDueFollowUps, sendAskBatch } from "@/lib/store";
import type { Channel } from "@/lib/types";

export async function POST(
  request: Request,
  context: { params: Promise<{ slug: string }> },
) {
  const { slug } = await context.params;
  const body = (await request.json()) as {
    action?: "register" | "ask" | "followups";
    name?: string;
    phone?: string;
    channel?: Channel;
    serviceNote?: string;
    count?: number;
  };

  try {
    if (body.action === "register") {
      if (!body.phone) {
        return NextResponse.json({ error: "phone required" }, { status: 400 });
      }
      const customer = registerCustomer({
        businessSlug: slug,
        name: body.name || "Customer",
        phone: body.phone,
        channel: body.channel,
        serviceNote: body.serviceNote,
      });
      return NextResponse.json({ customer });
    }

    if (body.action === "followups") {
      const result = runDueFollowUps(slug);
      return NextResponse.json(result);
    }

    // default: ask batch
    const result = sendAskBatch(
      Math.min(Math.max(body.count ?? 3, 1), 10),
      body.channel === "sms" ? "sms" : "whatsapp",
      slug,
    );
    return NextResponse.json(result);
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed" },
      { status: 400 },
    );
  }
}
