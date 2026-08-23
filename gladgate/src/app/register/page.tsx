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
  const [ecocashNumber, setEcocashNumber] = useState("");
  const [payNow, setPayNow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const tip = useMemo(() => {
    if (trialCode.trim()) return `Trial code ${trialCode.trim().toUpperCase()} will be applied.`;
    if (payNow) return "Demo EcoCash $3 confirmation will activate your plan.";
    return "Without a code you still get a 7-day soft trial + link & QR.";
  }, [trialCode, payNow]);

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
          ecocashNumber: ecocashNumber || undefined,
          payNow,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Registration failed");
      router.push(data.business.dashboardPath);
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
          Get a review link + QR code. Happy reviews are posted by Mashtech
          tagging your page. <strong>$3 / month on EcoCash</strong> after trial.
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
          WhatsApp / EcoCash phone
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
          Trial code (pre-launch)
          <input
            className={styles.input}
            value={trialCode}
            onChange={(e) => setTrialCode(e.target.value)}
            placeholder="MASHTECH14"
          />
        </label>

        <label className={styles.check}>
          <input
            type="checkbox"
            checked={payNow}
            onChange={(e) => setPayNow(e.target.checked)}
          />
          Pay $3 now with EcoCash (demo)
        </label>

        {payNow ? (
          <label className={styles.label}>
            EcoCash number
            <input
              className={styles.input}
              value={ecocashNumber}
              onChange={(e) => setEcocashNumber(e.target.value)}
              placeholder="07…"
              required={payNow}
            />
          </label>
        ) : null}

        <p className={styles.tip}>{tip}</p>
        {error ? <p className={styles.error}>{error}</p> : null}

        <button className={styles.submit} type="submit" disabled={busy}>
          {busy ? "Creating…" : "Create link & QR"}
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
