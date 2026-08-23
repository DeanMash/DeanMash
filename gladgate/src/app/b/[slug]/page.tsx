import { getBusinessBySlug } from "@/lib/store";
import { notFound } from "next/navigation";
import PublicReviewClient from "./PublicReviewClient";

export const dynamic = "force-dynamic";

export default async function BusinessReviewPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const business = getBusinessBySlug(slug);
  if (!business) notFound();
  return (
    <PublicReviewClient slug={business.slug} businessName={business.name} />
  );
}
