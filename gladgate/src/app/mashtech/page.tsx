import { getMashtechSnapshot } from "@/lib/store";
import MashtechClient from "./MashtechClient";

export const dynamic = "force-dynamic";

export default async function MashtechPage({
  searchParams,
}: {
  searchParams: Promise<{ project?: string }>;
}) {
  const { project } = await searchParams;
  const snapshot = getMashtechSnapshot();
  return (
    <MashtechClient initial={snapshot} highlightSlug={project} />
  );
}
