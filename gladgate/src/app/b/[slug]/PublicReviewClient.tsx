"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import styles from "../../form.module.css";

export default function PublicReviewClient({
  slug,
  businessName,
}: {
  slug: string;
  businessName: string;
}) {
  const [customerName, setCustomerName] = useState("");
  const [phone, setPhone] = useState("");
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    message: string;
    disposition: string;
    mashtechNote?: string;
  } | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`/api/businesses/${slug}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customerName, phone, rating, comment }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Could not submit");
      setResult({
        message: data.message,
        disposition: data.pulse.disposition,
        mashtechNote: data.mashtechNote,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not submit");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={styles.page}>
      <form className={styles.card} onSubmit={onSubmit}>
        <div className={styles.brand}>GladGate</div>
        {result ? (
          <>
            <h2
              className={`${styles.resultTitle} ${
                result.disposition === "routed_public" ? styles.ok : styles.held
              }`}
            >
              {result.disposition === "routed_public"
                ? "Thank you — Mashtech will share this"
                : "Kept private — owner will follow up"}
            </h2>
            <p className={styles.sub}>{result.message}</p>
            {result.mashtechNote ? (
              <p className={styles.tip}>{result.mashtechNote}</p>
            ) : null}
          </>
        ) : (
          <>
            <h1>How was {businessName}?</h1>
            <p className={styles.sub}>
              Happy notes can be posted by Mashtech tagging their page. Critical
              feedback stays private.
            </p>

            <label className={styles.label}>
              Your name
              <input
                className={styles.input}
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                placeholder="Optional"
              />
            </label>

            <label className={styles.label}>
              WhatsApp number (for follow-ups)
              <input
                className={styles.input}
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+26377… optional"
              />
            </label>

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

            <label className={styles.label}>
              Comment
              <textarea
                className={styles.textarea}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="What went well — or what should they fix privately?"
              />
            </label>

            {error ? <p className={styles.error}>{error}</p> : null}
            <button className={styles.submit} type="submit" disabled={busy}>
              {busy ? "Sending…" : "Send review"}
            </button>
          </>
        )}
        <p className={styles.footerLinks}>
          <Link href={`/b/${slug}/dashboard`}>Owner dashboard</Link>
        </p>
      </form>
    </div>
  );
}
