import Image from "next/image";
import Link from "next/link";
import { PLANS } from "@/lib/pricing";
import { VERTICALS } from "@/lib/verticals";
import styles from "./page.module.css";

export default function HomePage() {
  return (
    <div className={styles.shell}>
      <header className={styles.nav}>
        <div className={styles.brand}>GladGate</div>
        <nav className={styles.navLinks}>
          <a href="#how">How it works</a>
          <a href="#businesses">Businesses</a>
          <a href="#pricing">Pricing</a>
          <Link className={styles.navCta} href="/dashboard">
            Open demo
          </Link>
        </nav>
      </header>

      <section className={styles.hero} aria-label="GladGate hero">
        <div className={styles.heroMedia}>
          <Image
            src="https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=2000&q=80"
            alt="Busy restaurant floor at service time"
            fill
            priority
            sizes="100vw"
            style={{ objectFit: "cover" }}
          />
          <div className={styles.heroShade} />
        </div>
        <div className={styles.heroCopy}>
          <p className={styles.heroBrand}>GladGate</p>
          <h1 className={styles.heroHeadline}>
            Ask every happy customer. Stop one-star essays at the gate.
          </h1>
          <p className={styles.heroSupport}>
            WhatsApp-first review routing for shops that cannot afford a public
            meltdown overnight.
          </p>
          <div className={styles.ctaRow}>
            <Link className={styles.btnPrimary} href="/dashboard">
              Try the live demo
            </Link>
            <a className={styles.btnGhost} href="#pricing">
              See $500–$1,500 plans
            </a>
          </div>
        </div>
      </section>

      <section className={styles.section} id="how">
        <div className={styles.sectionNarrow}>
          <div className={styles.sectionHead}>
            <h2>Happy voices go public. Hurt feelings stay private.</h2>
            <p>
              Most owners never ask for reviews. Angry customers still write
              them — at midnight. GladGate flips that.
            </p>
          </div>
          <div className={styles.problem}>
            <blockquote className={styles.quote}>
              Unhappy clients write one-star essays at midnight. GladGate asks
              the quiet majority while they still feel good — and flags risk
              before anything goes live.
              <span>Built for Zimbabwe and similar markets where WhatsApp is the shop floor.</span>
            </blockquote>
            <div className={styles.flow}>
              <div className={styles.flowStep}>
                <strong>1. Auto-ask after the visit</strong>
                <p>
                  POS, booking, or staff tap sends a WhatsApp (or SMS) pulse:
                  “How did we do today?”
                </p>
              </div>
              <div className={styles.flowStep}>
                <strong>2. Route the glad ones</strong>
                <p>
                  Scores of 4–5 with clean language get a one-tap path to Google
                  or Facebook.
                </p>
              </div>
              <div className={styles.flowStep}>
                <strong>3. Hold the hurt ones</strong>
                <p>
                  Low scores and complaint language never post publicly. Owners
                  get an alert and a recovery path first.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className={styles.section} id="businesses">
        <div className={styles.sectionNarrow}>
          <div className={styles.sectionHead}>
            <h2>Built for the businesses that live on reputation.</h2>
            <p>
              Restaurants, workshops, salons, and the everyday shops that carry
              neighbourhood trust across developing markets.
            </p>
          </div>
          <div className={styles.verticalGrid}>
            {VERTICALS.map((vertical) => (
              <article key={vertical.id} className={styles.verticalItem}>
                <h3>{vertical.name}</h3>
                <p>{vertical.blurb}</p>
                <small>{vertical.askMoment}</small>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.section} id="pricing">
        <div className={styles.sectionNarrow}>
          <div className={styles.sectionHead}>
            <h2>Pricing that matches a reputation budget.</h2>
            <p>
              $500 to $1,500 per month in USD — billable by bank transfer or
              EcoCash for Zimbabwe operators.
            </p>
          </div>
          <div className={styles.pricingGrid}>
            {PLANS.map((plan) => (
              <article
                key={plan.id}
                className={`${styles.plan} ${
                  plan.id === "street" ? styles.planFeatured : ""
                }`}
              >
                <div className={styles.planName}>{plan.name}</div>
                <div className={styles.price}>
                  ${plan.priceUsd}
                  <span>/mo</span>
                </div>
                <p className={styles.planMeta}>
                  {plan.tagline}
                  <br />
                  {plan.locations} · {plan.bestFor}
                </p>
                <ul>
                  {plan.features.map((feature) => (
                    <li key={feature}>{feature}</li>
                  ))}
                </ul>
                <Link
                  className={
                    plan.id === "street" ? styles.btnPrimary : styles.btnDark
                  }
                  href="/dashboard"
                >
                  Start with demo
                </Link>
              </article>
            ))}
          </div>
          <p className={styles.marketNote}>
            Designed for multi-staff restaurants, panel beaters, salon groups,
            pharmacies, lodges, clinics, hardware counters, and car washes in
            Zimbabwe, Zambia, Botswana, Malawi, and similar markets — where a
            public one-star can cost more than a month of GladGate.
          </p>
        </div>
      </section>

      <footer className={styles.footer}>
        <div>
          <strong>GladGate</strong>
          <div>Ask happy. Hold hurt. Grow stars.</div>
        </div>
        <div>
          <Link href="/dashboard">Live demo dashboard →</Link>
        </div>
      </footer>
    </div>
  );
}
