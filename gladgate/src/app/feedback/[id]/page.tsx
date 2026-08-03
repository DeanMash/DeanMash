import { getPulse } from "@/lib/store";
import FeedbackClient from "./FeedbackClient";

export const dynamic = "force-dynamic";

export default async function FeedbackPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const pulse = getPulse(id) ?? null;
  return <FeedbackClient pulseId={id} initialPulse={pulse} />;
}
