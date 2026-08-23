import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { isMashtechAuthed, MASHTECH_COOKIE } from "@/lib/auth";
import { getMashtechSnapshot } from "@/lib/store";
import MashtechClient from "./MashtechClient";

export const dynamic = "force-dynamic";

export default async function MashtechPage({
  searchParams,
}: {
  searchParams: Promise<{ project?: string }>;
}) {
  const jar = await cookies();
  if (!isMashtechAuthed(jar.get(MASHTECH_COOKIE)?.value)) {
    redirect("/mashtech/login");
  }

  const { project } = await searchParams;
  const snapshot = getMashtechSnapshot();
  return <MashtechClient initial={snapshot} highlightSlug={project} />;
}
