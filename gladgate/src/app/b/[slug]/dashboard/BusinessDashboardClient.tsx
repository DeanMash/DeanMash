"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import styles from "./biz.module.css";

type Snapshot = {
  business: {
    name: string;
    slug: string;
    city: string;
    country: string;
    vertical: string;
    facebookHandle: string;
    subscriptionStatus: string;
    freeTrialUsed?: boolean;
    trialCode?: string;
    trialEndsAt?: string;
    nextBillingAt?: string;
    lastPaymentAt?: string;
    planId: string;
    reviewPath: string;
    dashboardPath: string;
  };
  reviewUrl: string;
  dashboardUrl: string;
  qrDataUrl: string;
  pendingPayment: {
    reference: string;
    amountUsd: number;
    ecocashNumber: string;
    status: string;
    createdAt: string;
  } | null;
  ecocashInstructions: {
    name: string;
    merchantCode: string;
    instruction: string;
  };
  monthlyAmountUsd: number;
  pulses: Array<{
    id: string;
    customerName: string;
    phone: string;
    channel: string;
    serviceNote: string;
    rating?: number;
    comment?: string;
    disposition: string;
  }>;
  flagged: Array<{
    id: string;
    customerName: string;
    rating: number;
    comment: string;
    flags: string[];
    status: string;
  }>;
  customers: Array<{
    id: string;
    name: string;
    phone: string;
    nextFollowUpAt: string;
    followUpCount: number;
    lastServiceNote: string;
  }>;
  socialPosts: Array<{
    id: string;
    body: string;
    tagHandle: string;
    status: string;
    createdAt: string;
  }>;
  stats: {
    customers: number;
    asksSent: number;
    publicRouted: number;
    heldPrivate: number;
    socialQueued: number;
    socialPosted: number;
    happyRate: number;
    followUpsDue: number;
  };
};

function badgeClass(disposition: string) {
  if (disposition === "routed_public") return styles.public;
  if (disposition === "held_private") return styles.private;
  return styles.awaiting;
}

function badgeLabel(disposition: string) {
  if (disposition === "routed_public") return "Routed public";
  if (disposition === "held_private") return "Held private";
  return "Awaiting reply";
}

export default function BusinessDashboardClient({
  initial,
}: {
  initial: Snapshot;
}) {
  const [data, setData] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [custName, setCustName] = useState("");
  const [custPhone, setCustPhone] = useState("");
  const [custNote, setCustNote] = useState("");
  const [ecocash, setEcocash] = useState("");

  async function reload() {
    const res = await fetch(`/api/businesses/${data.business.slug}`, {
      cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to reload");
    setData(await res.json());
  }

  async function runAction(
    label: string,
    fn: () => Promise<void>,
  ) {
    setBusy(true);
    setMessage(null);
    try {
      await fn();
      await reload();
      setMessage(label);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Action failed");
    } finally {
      setBusy(false);
    }
  }

  async function registerCustomer(e: FormEvent) {
    e.preventDefault();
    await runAction("Customer registered for automatic follow-ups.", async () => {
      const res = await fetch(
        `/api/businesses/${data.business.slug}/customers`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            action: "register",
            name: custName,
            phone: custPhone,
            serviceNote: custNote,
          }),
        },
      );
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || "Failed");
      setCustName("");
      setCustPhone("");
      setCustNote("");
    });
  }

  return (
    <div className={styles.page}>
      <div className={styles.top}>
        <div>
          <div className={styles.brandLine}>GladGate · Mashtech</div>
          <h1>{data.business.name}</h1>
          <p className={styles.meta}>
            {data.business.city}, {data.business.country} ·{" "}
            {data.business.vertical.replace("_", " ")} ·{" "}
            <strong>{data.business.subscriptionStatus}</strong>
            {data.business.trialEndsAt &&
            data.business.subscriptionStatus === "trial"
              ? ` · trial ends ${new Date(data.business.trialEndsAt).toLocaleDateString()}`
              : ""}
            {data.business.nextBillingAt &&
            data.business.subscriptionStatus === "active"
              ? ` · next bill ${new Date(data.business.nextBillingAt).toLocaleDateString()}`
              : ""}
            {" · "}${data.monthlyAmountUsd}/mo EcoCash
          </p>
        </div>
        <div className={styles.actions}>
          <button
            className={styles.btn}
            disabled={busy}
            onClick={() =>
              runAction("WhatsApp asks sent.", async () => {
                await fetch(`/api/businesses/${data.business.slug}/customers`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ action: "ask", count: 3 }),
                });
              })
            }
          >
            Auto-ask customers
          </button>
          <button
            className={styles.btnSoft}
            disabled={busy}
            onClick={() =>
              runAction("Due follow-ups sent.", async () => {
                await fetch(`/api/businesses/${data.business.slug}/customers`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ action: "followups" }),
                });
              })
            }
          >
            Run follow-ups ({data.stats.followUpsDue})
          </button>
          <button
            className={styles.btnSoft}
            disabled={busy}
            onClick={() =>
              runAction("Mashtech published queued posts.", async () => {
                const res = await fetch(
                  `/api/businesses/${data.business.slug}/actions`,
                  {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ action: "publish_social" }),
                  },
                );
                const json = await res.json();
                if (!res.ok) throw new Error(json.error || "Failed");
              })
            }
          >
            Mashtech post queue
          </button>
          <Link className={styles.btnSoft} href={data.business.reviewPath}>
            Open review page
          </Link>
          <Link className={styles.btnSoft} href="/">
            Home
          </Link>
        </div>
      </div>

      {message ? <p className={styles.empty}>{message}</p> : null}

      <div className={styles.stats}>
        <div className={styles.stat}>
          <strong>{data.stats.customers}</strong>
          <span>Registered customers</span>
        </div>
        <div className={styles.stat}>
          <strong>
            {data.stats.averageRating ?? "—"}
          </strong>
          <span>Avg rating ({data.stats.reviewCount ?? 0})</span>
        </div>
        <div className={styles.stat}>
          <strong>{data.stats.publicRouted}</strong>
          <span>Happy → Mashtech</span>
        </div>
        <div className={styles.stat}>
          <strong>{data.stats.heldPrivate}</strong>
          <span>Flagged private</span>
        </div>
        <div className={styles.stat}>
          <strong>{data.stats.socialPosted}</strong>
          <span>Social posts live</span>
        </div>
      </div>

      <div className={styles.grid}>
        <section className={styles.panel}>
          <h2>Your link & QR code</h2>
          <div className={styles.qrWrap}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={data.qrDataUrl} alt={`QR for ${data.business.name}`} />
            <p className={styles.sub}>
              Print this for the counter. Customers scan → leave a review on
              your GladGate page.
            </p>
            <div className={styles.linkBox}>{data.reviewUrl}</div>
            <div className={styles.linkBox}>
              Owner dashboard: {data.dashboardUrl}
            </div>
          </div>

          <h2>Register a customer</h2>
          <form onSubmit={registerCustomer}>
            <div className={styles.formRow}>
              <input
                placeholder="Customer name"
                value={custName}
                onChange={(e) => setCustName(e.target.value)}
                required
              />
              <input
                placeholder="WhatsApp +263…"
                value={custPhone}
                onChange={(e) => setCustPhone(e.target.value)}
                required
              />
              <input
                placeholder="Service note"
                value={custNote}
                onChange={(e) => setCustNote(e.target.value)}
              />
            </div>
            <button className={styles.btn} type="submit" disabled={busy}>
              Save for automatic follow-ups
            </button>
          </form>

          {data.business.subscriptionStatus !== "active" ? (
            <div style={{ marginTop: "1.25rem" }}>
              <h2>EcoCash ${data.monthlyAmountUsd} / month</h2>
              <p className={styles.sub}>
                {data.business.freeTrialUsed
                  ? "Your one free trial is active. After it ends, pay on EcoCash — monthly billing starts only when Mashtech confirms payment."
                  : "Pay on EcoCash. Monthly billing starts only when Mashtech confirms payment."}
              </p>

              {data.pendingPayment ? (
                <div className={styles.item}>
                  <div className={styles.name}>Payment pending confirmation</div>
                  <div className={styles.sub}>
                    Pay ${data.pendingPayment.amountUsd} to{" "}
                    {data.ecocashInstructions.name} ({data.ecocashInstructions.merchantCode})
                    <br />
                    Reference: <strong>{data.pendingPayment.reference}</strong>
                    <br />
                    EcoCash: {data.pendingPayment.ecocashNumber}
                    <br />
                    {data.ecocashInstructions.instruction}
                  </div>
                  <p className={styles.sub} style={{ marginTop: "0.5rem" }}>
                    Waiting for Mashtech to receive EcoCash confirmation…
                  </p>
                  <button
                    className={styles.btnSoft}
                    type="button"
                    disabled={busy}
                    onClick={() =>
                      runAction("Status refreshed.", async () => {})
                    }
                  >
                    Refresh status
                  </button>
                </div>
              ) : (
                <>
                  <div className={styles.formRow}>
                    <input
                      placeholder="Your EcoCash number (07…)"
                      value={ecocash}
                      onChange={(e) => setEcocash(e.target.value)}
                    />
                  </div>
                  <button
                    className={styles.btnWarn}
                    type="button"
                    disabled={busy || !ecocash.trim()}
                    onClick={() =>
                      runAction("EcoCash payment request created.", async () => {
                        const res = await fetch(
                          `/api/businesses/${data.business.slug}/actions`,
                          {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                              action: "request_payment",
                              ecocashNumber: ecocash,
                            }),
                          },
                        );
                        const json = await res.json();
                        if (!res.ok) throw new Error(json.error || "Failed");
                      })
                    }
                  >
                    Request EcoCash payment
                  </button>
                </>
              )}
            </div>
          ) : (
            <div style={{ marginTop: "1.25rem" }}>
              <h2>EcoCash plan active</h2>
              <p className={styles.sub}>
                Last confirmed payment activates monthly billing until{" "}
                {data.business.nextBillingAt
                  ? new Date(data.business.nextBillingAt).toLocaleDateString()
                  : "renewal"}
                .
              </p>
            </div>
          )}
        </section>

        <section className={styles.panel}>
          <h2>Pulses, flags & Mashtech posts</h2>
          <div className={styles.list}>
            {data.pulses.length === 0 ? (
              <p className={styles.empty}>
                No reviews yet. Share your QR, register customers, or run
                auto-ask / follow-ups.
              </p>
            ) : (
              data.pulses.map((pulse) => (
                <article key={pulse.id} className={styles.item}>
                  <div className={styles.row}>
                    <div>
                      <div className={styles.name}>{pulse.customerName}</div>
                      <div className={styles.sub}>
                        {pulse.serviceNote}
                        <br />
                        {pulse.channel.toUpperCase()} · {pulse.phone || "no phone"}
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
                  {pulse.disposition === "awaiting_pulse" ? (
                    <Link
                      className={styles.sub}
                      href={`/feedback/${pulse.id}`}
                      style={{ fontWeight: 700, color: "var(--leaf)" }}
                    >
                      Open customer reply →
                    </Link>
                  ) : null}
                </article>
              ))
            )}
          </div>

          <h2 style={{ marginTop: "1.25rem" }}>Flagged before public</h2>
          <div className={styles.list}>
            {data.flagged.length === 0 ? (
              <p className={styles.empty}>No private flags yet.</p>
            ) : (
              data.flagged.map((flag) => (
                <article key={flag.id} className={`${styles.item} ${styles.flag}`}>
                  <div className={styles.name}>
                    {flag.customerName} · {flag.rating}/5
                  </div>
                  <div className={styles.sub}>
                    {flag.comment || "No comment"} · {flag.flags.join(", ")}
                  </div>
                </article>
              ))
            )}
          </div>

          <h2 style={{ marginTop: "1.25rem" }}>
            Mashtech social queue ({data.stats.socialQueued} waiting)
          </h2>
          <div className={styles.list}>
            {data.socialPosts.length === 0 ? (
              <p className={styles.empty}>
                Happy reviews appear here for Mashtech to post, tagging{" "}
                {data.business.facebookHandle}.
              </p>
            ) : (
              data.socialPosts.map((post) => (
                <article key={post.id} className={styles.item}>
                  <div className={styles.row}>
                    <div className={styles.name}>Tag {post.tagHandle}</div>
                    <span
                      className={`${styles.badge} ${
                        post.status === "posted" ? styles.public : styles.awaiting
                      }`}
                    >
                      {post.status}
                    </span>
                  </div>
                  <pre className={styles.pre}>{post.body}</pre>
                </article>
              ))
            )}
          </div>

          <h2 style={{ marginTop: "1.25rem" }}>Registered customers</h2>
          <div className={styles.list}>
            {data.customers.length === 0 ? (
              <p className={styles.empty}>
                Add customers so GladGate can run automatic checks and follow-ups.
              </p>
            ) : (
              data.customers.map((c) => (
                <article key={c.id} className={styles.item}>
                  <div className={styles.name}>
                    {c.name} · {c.phone}
                  </div>
                  <div className={styles.sub}>
                    {c.lastServiceNote} · follow-ups {c.followUpCount} · next{" "}
                    {new Date(c.nextFollowUpAt).toLocaleString()}
                  </div>
                </article>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
