"use client";

import Link from "next/link";
import { useState } from "react";
import styles from "./dashboard.module.css";

type Pulse = {
  id: string;
  customerName: string;
  phone: string;
  channel: string;
  serviceNote: string;
  createdAt: string;
  rating?: number;
  comment?: string;
  disposition: "routed_public" | "held_private" | "awaiting_pulse";
  flags: string[];
};

type Flagged = {
  id: string;
  customerName: string;
  rating: number;
  comment: string;
  flags: string[];
  status: "open" | "recovering" | "resolved";
  createdAt: string;
};

type Snapshot = {
  business: {
    name: string;
    city: string;
    country: string;
    vertical: string;
    planId: string;
  };
  pulses: Pulse[];
  flagged: Flagged[];
  stats: {
    asksSent: number;
    publicRouted: number;
    heldPrivate: number;
    happyRate: number;
  };
};

const FLAG_LABELS: Record<string, string> = {
  low_score: "Low score",
  complaint_language: "Complaint language",
  refund_threat: "Refund / legal threat",
  safety_concern: "Safety concern",
};

function badgeClass(disposition: Pulse["disposition"]) {
  if (disposition === "routed_public") return styles.public;
  if (disposition === "held_private") return styles.private;
  return styles.awaiting;
}

function badgeLabel(disposition: Pulse["disposition"]) {
  if (disposition === "routed_public") return "Routed public";
  if (disposition === "held_private") return "Held private";
  return "Awaiting reply";
}

export default function DashboardClient({
  initialData,
}: {
  initialData: Snapshot;
}) {
  const [data, setData] = useState<Snapshot>(initialData);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    const res = await fetch("/api/demo", { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to load demo");
    setData(await res.json());
  }

  async function sendAsks(channel: "whatsapp" | "sms") {
    setBusy(true);
    setError(null);
    try {
      await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ count: 3, channel }),
      });
      await load();
    } catch {
      setError("Could not send asks");
    } finally {
      setBusy(false);
    }
  }

  async function reset() {
    setBusy(true);
    try {
      await fetch("/api/demo", { method: "DELETE" });
      await load();
    } finally {
      setBusy(false);
    }
  }

  async function updateFlag(
    flagId: string,
    status: Flagged["status"],
  ) {
    await fetch("/api/flags", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ flagId, status }),
    });
    await load();
  }

  return (
    <div className={styles.page}>
      <div className={styles.top}>
        <div>
          <div className={styles.brandLine}>GladGate</div>
          <h1>{data.business.name} control room</h1>
          <p className={styles.meta}>
            {data.business.city}, {data.business.country} ·{" "}
            {data.business.vertical.replace("_", " ")} · {data.business.planId}{" "}
            plan
          </p>
        </div>
        <div className={styles.actions}>
          <button
            className={styles.btn}
            disabled={busy}
            onClick={() => sendAsks("whatsapp")}
          >
            Auto-ask 3 via WhatsApp
          </button>
          <button
            className={styles.btnSoft}
            disabled={busy}
            onClick={() => sendAsks("sms")}
          >
            Ask via SMS
          </button>
          <button className={styles.btnWarn} disabled={busy} onClick={reset}>
            Reset demo
          </button>
          <Link className={styles.btnSoft} href="/">
            ← Home
          </Link>
        </div>
      </div>

      {error ? <p className={styles.empty}>{error}</p> : null}

      <div className={styles.stats}>
        <div className={styles.stat}>
          <strong>{data.stats.asksSent}</strong>
          <span>Asks sent</span>
        </div>
        <div className={styles.stat}>
          <strong>{data.stats.publicRouted}</strong>
          <span>Happy → public</span>
        </div>
        <div className={styles.stat}>
          <strong>{data.stats.heldPrivate}</strong>
          <span>Flagged private</span>
        </div>
        <div className={styles.stat}>
          <strong>{data.stats.happyRate}%</strong>
          <span>Glad rate</span>
        </div>
      </div>

      <div className={styles.grid}>
        <section className={styles.panel}>
          <h2>Customer pulses</h2>
          <div className={styles.list}>
            {data.pulses.length === 0 ? (
              <p className={styles.empty}>
                No asks yet. Hit <strong>Auto-ask 3 via WhatsApp</strong> to
                simulate end-of-visit messages, then open a customer link and
                reply as them.
              </p>
            ) : (
              data.pulses.map((pulse) => (
                <article key={pulse.id} className={styles.pulse}>
                  <div className={styles.row}>
                    <div>
                      <div className={styles.name}>{pulse.customerName}</div>
                      <div className={styles.sub}>
                        {pulse.serviceNote}
                        <br />
                        {pulse.channel.toUpperCase()} · {pulse.phone}
                        {pulse.rating ? ` · ${pulse.rating}/5` : ""}
                      </div>
                    </div>
                    <span
                      className={`${styles.badge} ${badgeClass(
                        pulse.disposition,
                      )}`}
                    >
                      {badgeLabel(pulse.disposition)}
                    </span>
                  </div>
                  {pulse.comment ? (
                    <p className={styles.sub}>“{pulse.comment}”</p>
                  ) : null}
                  {pulse.flags.length > 0 ? (
                    <div className={styles.flagTags}>
                      {pulse.flags.map((flag) => (
                        <span key={flag} className={styles.tag}>
                          {FLAG_LABELS[flag] ?? flag}
                        </span>
                      ))}
                    </div>
                  ) : null}
                  {pulse.disposition === "awaiting_pulse" ? (
                    <div className={styles.links}>
                      <Link href={`/feedback/${pulse.id}`}>
                        Open customer reply →
                      </Link>
                    </div>
                  ) : null}
                </article>
              ))
            )}
          </div>
        </section>

        <section className={styles.panel}>
          <h2>Flagged before public</h2>
          <div className={styles.list}>
            {data.flagged.length === 0 ? (
              <p className={styles.empty}>
                Bad or risky replies appear here — never on Google. Try a 2-star
                reply with words like “terrible” or “refund”.
              </p>
            ) : (
              data.flagged.map((flag) => (
                <article key={flag.id} className={styles.flag}>
                  <div className={styles.row}>
                    <div>
                      <div className={styles.name}>
                        {flag.customerName} · {flag.rating}/5
                      </div>
                      <div className={styles.sub}>
                        {flag.comment || "No written comment"}
                      </div>
                    </div>
                  </div>
                  <div className={styles.flagTags}>
                    {flag.flags.map((item) => (
                      <span key={item} className={styles.tag}>
                        {FLAG_LABELS[item] ?? item}
                      </span>
                    ))}
                  </div>
                  <select
                    className={styles.statusSelect}
                    value={flag.status}
                    onChange={(e) =>
                      updateFlag(
                        flag.id,
                        e.target.value as Flagged["status"],
                      )
                    }
                  >
                    <option value="open">Open — owner alerted</option>
                    <option value="recovering">Recovering</option>
                    <option value="resolved">Resolved privately</option>
                  </select>
                </article>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
