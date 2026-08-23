import { NextResponse } from "next/server";
import { absoluteUrl, qrDataUrl } from "@/lib/qr";
import { getBusinessSnapshot } from "@/lib/store";

export async function GET(
  request: Request,
  context: { params: Promise<{ slug: string }> },
) {
  const { slug } = await context.params;
  const snap = getBusinessSnapshot(slug);
  if (!snap) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  const origin = new URL(request.url).origin;
  const reviewUrl = absoluteUrl(snap.business.reviewPath, origin);
  const dashboardUrl = absoluteUrl(snap.business.dashboardPath, origin);
  const qr = await qrDataUrl(reviewUrl);

  return NextResponse.json({
    ...snap,
    reviewUrl,
    dashboardUrl,
    qrDataUrl: qr,
  });
}
