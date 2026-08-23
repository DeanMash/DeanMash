import { getDemoSnapshot } from "@/lib/store";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

/** Legacy demo route → seeded Amanzi Grill business dashboard. */
export default function DashboardPage() {
  const snap = getDemoSnapshot();
  redirect(snap.business.dashboardPath);
}
