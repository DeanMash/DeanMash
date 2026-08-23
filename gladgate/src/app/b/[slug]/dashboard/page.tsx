import { absoluteUrl, qrDataUrl } from "@/lib/qr";
import { getBusinessSnapshot } from "@/lib/store";
import { notFound } from "next/navigation";
import { headers } from "next/headers";
import BusinessDashboardClient from "./BusinessDashboardClient";

export const dynamic = "force-dynamic";

export default async function BusinessDashboardPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const snap = getBusinessSnapshot(slug);
  if (!snap) notFound();

  const h = await headers();
  const host = h.get("x-forwarded-host") || h.get("host") || "localhost:3000";
  const proto = h.get("x-forwarded-proto") || "http";
  const origin = `${proto}://${host}`;
  const reviewUrl = absoluteUrl(snap.business.reviewPath, origin);
  const dashboardUrl = absoluteUrl(snap.business.dashboardPath, origin);
  const qr = await qrDataUrl(reviewUrl);

  return (
    <BusinessDashboardClient
      initial={{
        ...snap,
        reviewUrl,
        dashboardUrl,
        qrDataUrl: qr,
      }}
    />
  );
}
