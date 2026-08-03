import { getDemoSnapshot } from "@/lib/store";
import DashboardClient from "./DashboardClient";

export const dynamic = "force-dynamic";

export default function DashboardPage() {
  const initial = getDemoSnapshot();
  return <DashboardClient initialData={initial} />;
}
