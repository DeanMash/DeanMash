"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import styles from "./mashtech.module.css";

type Snapshot = {
  projects: Array<{
    business: {
      name: string;
      slug: string;
      city: string;
      country: string;
      vertical: string;
      facebookHandle: string;
      subscriptionStatus: string;
      trialEndsAt?: string;
      nextBillingAt?: string;
      reviewPath: string;
      dashboardPath: string;
      ownerPhone: string;
    };
    stats: {
      postsQueued: number;
      postsLive: number;
      reviews: number;
      averageRating: number | null;
      flaggedOpen: number;
      paymentsPending: number;
    };
    rating: {
      average: number | null;
      count: number;
      starsLabel: string;
    };
  }>;
  posts: Array<{
    id: string;
    kind: string;
    status: string;
    readyCaption: string;
    body: string;
    tagHandle: string;
    businessName: string;
    businessSlug: string;
    reviewPath: string;
    imageUrl: string;
    createdAt: string;
  }>;
  pendingPayments: Array<{
    id: string;
    reference: string;
    amountUsd: number;
    ecocashNumber: string;
    businessName: string;
    businessSlug: string;
    createdAt: string;
  }>;
  stats: {
    projects: number;
    postsQueued: number;
    postsLive: number;
    paymentsPending: number;
    trials: number;
    active: number;
    averageRating: number | null;
    totalReviews: number;
  };
};

function statusClass(status: string) {
  if (status === "active") return styles.active;
  if (status === "trial") return styles.trial;
  return styles.pastdue;
}

export default function MashtechClient({
  initial,
  highlightSlug,
}: {
  initial: Snapshot;
  highlightSlug?: string;
}) {
  const [data, setData] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(
    highlightSlug
      ? `New project “${highlightSlug}” registered — launch post is ready to use.`
      : null,
  );

  const highlight = useMemo(
    () => highlightSlug?.toLowerCase(),
    [highlightSlug],
  );

  async function run(
    label: string,
    body: Record<string, string>,
  ) {
    setBusy(true);
    setMessage(null);
    try {
      const res = await fetch("/api/mashtech", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || "Failed");
      if (json.snapshot) setData(json.snapshot);
      setMessage(json.message || label);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  async function refresh() {
    setBusy(true);
    try {
      const res = await fetch("/api/mashtech", { cache: "no-store" });
      if (!res.ok) throw new Error("Failed to refresh");
      setData(await res.json());
      setMessage("Dashboard refreshed.");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  async function copyCaption(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setMessage("Caption copied — paste on Facebook / WhatsApp Status.");
    } catch {
      setMessage("Could not copy — select the caption manually.");
    }
  }

  async function logout() {
    await fetch("/api/mashtech/login", { method: "DELETE" });
    window.location.href = "/mashtech/login";
  }

  return (
    <div className={styles.page}>
      <div className={styles.top}>
        <div>
          <div className={styles.brand}>Mashtech · GladGate control</div>
          <h1>All projects & auto posts</h1>
          <p className={styles.meta}>
            Every registered shop lands here. Launch and review captions are
            created automatically for Mashtech to publish.
          </p>
        </div>
        <div className={styles.actions}>
          <button
            className={styles.btn}
            disabled={busy || data.stats.postsQueued === 0}
            onClick={() => run("Published all.", { action: "publish_all" })}
          >
            Publish all queued ({data.stats.postsQueued})
          </button>
          <button className={styles.btnSoft} disabled={busy} onClick={refresh}>
            Refresh
          </button>
          <button className={styles.btnSoft} type="button" onClick={logout}>
            Sign out
          </button>
          <Link className={styles.btnSoft} href="/register">
            Register shop
          </Link>
          <Link className={styles.btnSoft} href="/">
            Home
          </Link>
        </div>
      </div>

      {message ? <div className={styles.banner}>{message}</div> : null}

      <div className={styles.stats}>
        <div className={styles.stat}>
          <strong>{data.stats.projects}</strong>
          <span>Projects</span>
        </div>
        <div className={styles.stat}>
          <strong>{data.stats.postsQueued}</strong>
          <span>Posts ready</span>
        </div>
        <div className={styles.stat}>
          <strong>{data.stats.postsLive}</strong>
          <span>Posts live</span>
        </div>
        <div className={styles.stat}>
          <strong>{data.stats.paymentsPending}</strong>
          <span>Payments to confirm</span>
        </div>
        <div className={styles.stat}>
          <strong>
            {data.stats.averageRating ?? "—"}
          </strong>
          <span>Avg rating (all shops)</span>
        </div>
      </div>

      <div className={styles.grid}>
        <section className={styles.panel}>
          <h2>Projects</h2>
          <div className={styles.list}>
            {data.projects.length === 0 ? (
              <p className={styles.empty}>No shops registered yet.</p>
            ) : (
              data.projects.map((project) => (
                <article
                  key={project.business.slug}
                  className={`${styles.card} ${
                    highlight === project.business.slug
                      ? styles.cardHighlight
                      : ""
                  }`}
                >
                  <div className={styles.row}>
                    <div>
                      <div className={styles.name}>{project.business.name}</div>
                      <div className={styles.sub}>
                        {project.business.city} ·{" "}
                        {project.business.vertical.replace("_", " ")} ·{" "}
                        {project.business.facebookHandle}
                        <br />
                        <strong>{project.rating.starsLabel}</strong>
                        {" · "}
                        {project.stats.postsQueued} posts ready ·{" "}
                        owner {project.business.ownerPhone}
                      </div>
                    </div>
                    <span
                      className={`${styles.badge} ${statusClass(
                        project.business.subscriptionStatus,
                      )}`}
                    >
                      {project.business.subscriptionStatus}
                    </span>
                  </div>
                  <div className={styles.cardActions}>
                    <Link href={project.business.dashboardPath}>
                      Shop dashboard →
                    </Link>
                    <Link href={project.business.reviewPath}>Review page →</Link>
                  </div>
                </article>
              ))
            )}
          </div>

          <h2 style={{ marginTop: "1.4rem" }}>EcoCash to confirm</h2>
          <div className={styles.list}>
            {data.pendingPayments.length === 0 ? (
              <p className={styles.empty}>No pending EcoCash payments.</p>
            ) : (
              data.pendingPayments.map((pay) => (
                <article key={pay.id} className={styles.card}>
                  <div className={styles.name}>
                    {pay.businessName} · ${pay.amountUsd}
                  </div>
                  <div className={styles.sub}>
                    Ref <strong>{pay.reference}</strong> · EcoCash{" "}
                    {pay.ecocashNumber}
                  </div>
                  <div className={styles.cardActions}>
                    <button
                      type="button"
                      disabled={busy}
                      onClick={() =>
                        run("Payment confirmed.", {
                          action: "confirm_payment",
                          reference: pay.reference,
                        })
                      }
                    >
                      Confirm payment received →
                    </button>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>

        <section className={styles.panel}>
          <h2>Auto-created posts (ready to use)</h2>
          <div className={styles.list}>
            {data.posts.length === 0 ? (
              <p className={styles.empty}>
                Posts appear here when a shop registers (launch) or a happy
                review arrives.
              </p>
            ) : (
              data.posts.map((post) => (
                <article key={post.id} className={styles.card}>
                  <div className={styles.row}>
                    <div>
                      <div className={styles.name}>
                        {post.businessName} · {post.kind}
                      </div>
                      <div className={styles.sub}>
                        Tag {post.tagHandle} ·{" "}
                        {new Date(post.createdAt).toLocaleString()}
                      </div>
                    </div>
                    <span
                      className={`${styles.badge} ${
                        post.status === "posted" ? styles.posted : styles.queued
                      }`}
                    >
                      {post.status}
                    </span>
                  </div>
                  <pre className={styles.pre}>
                    {post.readyCaption || post.body}
                  </pre>
                  <a href={post.imageUrl} target="_blank" rel="noreferrer">
                    {/* Dynamic JPEG from API — not optimizable via next/image */}
                    <img
                      className={styles.preview}
                      src={post.imageUrl}
                      alt={`${post.businessName} social JPG`}
                    />
                  </a>
                  <div className={styles.cardActions}>
                    <button type="button" onClick={() => copyCaption(post.readyCaption || post.body)}>
                      Copy caption
                    </button>
                    <a href={post.imageUrl} download={`gladgate-${post.businessSlug}-${post.id}.jpg`}>
                      Download JPG
                    </a>
                    {post.status === "queued" ? (
                      <button
                        type="button"
                        disabled={busy}
                        onClick={() =>
                          run("Post published.", {
                            action: "publish_post",
                            postId: post.id,
                          })
                        }
                      >
                        Mark published
                      </button>
                    ) : null}
                    {post.reviewPath ? (
                      <Link href={post.reviewPath}>Review link →</Link>
                    ) : null}
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
