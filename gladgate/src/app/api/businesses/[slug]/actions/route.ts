import { NextResponse } from "next/server";
import { publishSocialQueue, requestEcoCashPayment } from "@/lib/store";

export async function POST(
  request: Request,
  context: { params: Promise<{ slug: string }> },
) {
  const { slug } = await context.params;
  const body = (await request.json()) as {
    action?: "publish_social" | "request_payment";
    ecocashNumber?: string;
  };

  try {
    if (body.action === "request_payment") {
      const result = requestEcoCashPayment({
        businessSlug: slug,
        ecocashNumber: body.ecocashNumber || "",
      });
      return NextResponse.json(result);
    }

    const result = publishSocialQueue(slug);
    return NextResponse.json({
      ...result,
      message: `Mashtech posted ${result.posted} review(s) tagging the business page.`,
    });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed" },
      { status: 400 },
    );
  }
}
