"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useMemo, useState } from "react";
import { VERTICALS } from "@/lib/verticals";
import styles from "../form.module.css";

function RegisterForm() {
  const router = useRouter();
  const params = useSearchParams();
  const presetCode = params.get("code") || "";

  const [name, setName] = useState("");
  const [vertical, setVertical] = useState(VERTICALS[0].id);
  const [city, setCity] = useState("Harare");
  const [ownerName, setOwnerName] = useState("");
  const [ownerPhone, setOwnerPhone] = useState("");
  const [facebookHandle, setFacebookHandle] = useState("");
  const [trialCode, setTrialCode] = useState(presetCode);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const tip = useMemo(() => {
    if (trialCode.trim()) {
      return `Trial code ${trialCode.trim().toUpperCase()} extends your one free trial. EcoCash $3/month starts only after Mashtech payment confirmation.`;
    }
    return "Every shop gets one free trial (14 days). After that, pay $3/month on EcoCash — activation only when payment is confirmed.";
  }, [trialCode]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          vertical,
          city,
          ownerName,
          ownerPhone,
          facebookHandle,
          trialCode: trialCode || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Registration failed");
      router.push(data.mashtechPath || `/mashtech?project=${data.business.slug}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={styles.page}>
      <form className={styles.card} onSubmit={onSubmit}>
        <div className={styles.brand}>GladGate · Mashtech</div>
        <h1>Register your small business</h1>
        <p className={styles.sub}>
          One free trial included. Get a review link + QR code. Happy reviews
          posted by Mashtech tagging your page.{" "}
          <strong>$3 / month on EcoCash</strong> after trial — only when payment
          is confirmed.
        </p>

        <label className={styles.label}>
          Business name
          <input
            className={styles.input}
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Amanzi Grill"
          />
        </label>

        <label className={styles.label}>
          Type of business
          <select
            className={styles.input}
            value={vertical}
            onChange={(e) => setVertical(e.target.value as typeof vertical)}
          >
            {VERTICALS.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name}
              </option>
            ))}
          </select>
        </label>

        <label className={styles.label}>
          City
          <input
            className={styles.input}
            value={city}
            onChange={(e) => setCity(e.target.value)}
          />
        </label>

        <label className={styles.label}>
          Owner name
          <input
            className={styles.input}
            value={ownerName}
            onChange={(e) => setOwnerName(e.target.value)}
            placeholder="Tariro"
          />
        </label>

        <label className={styles.label}>
          WhatsApp / phone
          <input
            className={styles.input}
            required
            value={ownerPhone}
            onChange={(e) => setOwnerPhone(e.target.value)}
            placeholder="+26377…"
          />
        </label>

        <label className={styles.label}>
          Facebook / social page to tag
          <input
            className={styles.input}
            required
            value={facebookHandle}
            onChange={(e) => setFacebookHandle(e.target.value)}
            placeholder="@YourShopHre"
          />
        </label>

        <label className={styles.label}>
          Trial code (optional — extends free trial once)
          <input
            className={styles.input}
            value={trialCode}
            onChange={(e) => setTrialCode(e.target.value)}
            placeholder="MASHTECH14"
          />
        </label>

        <p className={styles.tip}>{tip}</p>
        {error ? <p className={styles.error}>{error}</p> : null}

        <button className={styles.submit} type="submit" disabled={busy}>
          {busy ? "Creating…" : "Start free trial & get QR"}
        </button>

        <p className={styles.footerLinks}>
          <Link href="/trial">View trial codes & links</Link>
          {" · "}
          <Link href="/">Home</Link>
        </p>
      </form>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={<div className={styles.page}>Loading…</div>}>
      <RegisterForm />
    </Suspense>
  );
}
