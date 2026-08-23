import Link from "next/link";
import { TRIAL_OFFERS } from "@/lib/trials";
import styles from "../form.module.css";

export default function TrialPage() {
  return (
    <div className={styles.page}>
      <div className={styles.card} style={{ width: "min(100%, 640px)" }}>
        <div className={styles.brand}>GladGate · Pre-launch trials</div>
        <h1>Codes & links before we launch</h1>
        <p className={styles.sub}>
          Share these with small businesses for their **one free trial**. After trial,
          $3 / month on EcoCash — monthly billing starts only when Mashtech confirms payment. Mashtech posts happy
          reviews and tags their page.
        </p>

        <div className={styles.trialGrid}>
          {TRIAL_OFFERS.map((trial) => (
            <article key={trial.code} className={styles.trialItem}>
              <strong>{trial.label}</strong>
              <p className={styles.sub} style={{ marginBottom: 0 }}>
                {trial.description}
              </p>
              <div className={styles.code}>{trial.code}</div>
              <p className={styles.footerLinks} style={{ textAlign: "left" }}>
                <Link href={trial.registerPath}>
                  Open register link → {trial.registerPath}
                </Link>
              </p>
            </article>
          ))}
        </div>

        <p className={styles.footerLinks}>
          <Link href="/register">Register with default 14-day free trial</Link>
          {" · "}
          <Link href="/">Home</Link>
        </p>
      </div>
    </div>
  );
}
