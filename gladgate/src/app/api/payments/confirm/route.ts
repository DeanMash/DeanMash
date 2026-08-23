import { NextResponse } from "next/server";
import { confirmEcoCashPayment } from "@/lib/store";
import { verifyWebhookSecret } from "@/lib/billing";

/**
 * Mashtech / EcoCash webhook — monthly plan activates ONLY after confirmed payment.
 * Header: X-Mashtech-Secret (matches ECOCASH_WEBHOOK_SECRET env)
 */
export async function POST(request: Request) {
  const secret = request.headers.get("x-mashtech-secret");
  if (!verifyWebhookSecret(secret)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = (await request.json()) as {
    reference?: string;
    status?: "confirmed" | "failed";
  };

  if (!body.reference?.trim()) {
    return NextResponse.json({ error: "reference required" }, { status: 400 });
  }

  if (body.status === "failed") {
    return NextResponse.json({ ok: true, message: "Failure noted" });
  }

  try {
    const result = confirmEcoCashPayment({
      reference: body.reference,
      source: "ecocash_webhook",
    });
    return NextResponse.json({
      ok: true,
      alreadyConfirmed: result.alreadyConfirmed,
      business: {
        slug: result.business.slug,
        subscriptionStatus: result.business.subscriptionStatus,
        nextBillingAt: result.business.nextBillingAt,
      },
      payment: result.payment,
      message: result.alreadyConfirmed
        ? "Payment was already confirmed."
        : "EcoCash $3 confirmed — monthly plan activated.",
    });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Confirmation failed" },
      { status: 400 },
    );
  }
}
