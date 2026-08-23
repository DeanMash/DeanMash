"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useState } from "react";
import styles from "../../form.module.css";

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const next = params.get("next") || "/mashtech";
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/mashtech/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Login failed");
      router.push(next);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={styles.page}>
      <form className={styles.card} onSubmit={onSubmit}>
        <div className={styles.brand}>Mashtech · GladGate</div>
        <h1>Control room login</h1>
        <p className={styles.sub}>
          Restricted access for Mashtech operators. Set{" "}
          <code>MASHTECH_DASHBOARD_PASSWORD</code> before going live.
        </p>
        <label className={styles.label}>
          Password
          <input
            className={styles.input}
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Mashtech dashboard password"
          />
        </label>
        {error ? <p className={styles.error}>{error}</p> : null}
        <button className={styles.submit} type="submit" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
        <p className={styles.footerLinks}>
          <Link href="/">← Home</Link>
        </p>
      </form>
    </div>
  );
}

export default function MashtechLoginPage() {
  return (
    <Suspense fallback={<div className={styles.page}>Loading…</div>}>
      <LoginForm />
    </Suspense>
  );
}
