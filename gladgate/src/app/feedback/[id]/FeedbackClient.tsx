"use client";

import Link from "next/link";
import { useState } from "react";
import styles from "./feedback.module.css";

type Pulse = {
  id: string;
  customerName: string;
  serviceNote: string;
  disposition: string;
  rating?: number;
};

export default function FeedbackClient({
  pulseId,
  initialPulse,
}: {
  pulseId: string;
  initialPulse: Pulse | null;
}) {
  const [pulse] = useState<Pulse | null>(initialPulse);
  const [rating, setRating] = useState<number>(5);
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(
    initialPulse ? null : "This feedback link is invalid or expired.",
  );
  const [result, setResult] = useState<{
    message: string;
    disposition: string;
    publicReviewUrl: string | null;
  } | null>(() => {
    if (!initialPulse || initialPulse.disposition === "awaiting_pulse") {
      return null;
    }
    return {
      message:
        initialPulse.disposition === "routed_public"
          ? "You already sent a happy score — thank you."
          : "You already sent private feedback — thank you.",
      disposition: initialPulse.disposition,
      publicReviewUrl: null,
    };
  });

  async function submit() {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/pulse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pulseId, rating, comment }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Could not submit");
      setResult({
        message: data.message,
        disposition: data.pulse.disposition,
        publicReviewUrl: data.publicReviewUrl,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not submit");
    } finally {
      setBusy(false);
    }
  }

  if (error && !pulse) {
    return (
      <div className={styles.page}>
        <div className={styles.card}>
          <div className={styles.brand}>GladGate</div>
          <p>{error}</p>
          <Link className={styles.back} href="/dashboard">
            ← Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (!pulse) {
    return (
      <div className={styles.page}>
        <div className={styles.card}>Loading…</div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.brand}>GladGate</div>
        {result ? (
          <div className={styles.result}>
            <h2
              className={
                result.disposition === "routed_public" ? styles.ok : styles.held
              }
            >
              {result.disposition === "routed_public"
                ? "Ready for a public review"
                : "Kept private — owner alerted"}
            </h2>
            <p className={styles.sub}>{result.message}</p>
            {result.publicReviewUrl ? (
              <a
                className={styles.cta}
                href={result.publicReviewUrl}
                target="_blank"
                rel="noreferrer"
              >
                Leave public review
              </a>
            ) : null}
            <div>
              <Link className={styles.back} href="/dashboard">
                ← See owner dashboard
              </Link>
            </div>
          </div>
        ) : (
          <>
            <h1>Hi {pulse.customerName.split(" ")[0]} — how was it?</h1>
            <p className={styles.sub}>{pulse.serviceNote}</p>
            <div className={styles.stars} role="group" aria-label="Rating">
              {[1, 2, 3, 4, 5].map((value) => (
                <button
                  key={value}
                  type="button"
                  className={`${styles.star} ${
                    rating === value ? styles.starActive : ""
                  }`}
                  onClick={() => setRating(value)}
                >
                  {value}
                </button>
              ))}
            </div>
            <label className={styles.label} htmlFor="comment">
              Optional note
            </label>
            <textarea
              id="comment"
              className={styles.textarea}
              placeholder="Tell us what went well — or what we should fix privately."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
            />
            {error ? <p className={styles.sub}>{error}</p> : null}
            <button
              className={styles.submit}
              type="button"
              disabled={busy}
              onClick={submit}
            >
              {busy ? "Sending…" : "Send feedback"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
