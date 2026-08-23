import Image from "next/image";
import Link from "next/link";
import { PLANS } from "@/lib/pricing";
import { TRIAL_OFFERS } from "@/lib/trials";
import { VERTICALS } from "@/lib/verticals";
import styles from "./page.module.css";

export default function HomePage() {
  return (
    <div className={styles.shell}>
      <header className={styles.nav}>
        <div className={styles.brand}>GladGate</div>
        <nav className={styles.navLinks}>
          <a href="#how">How it works</a>
          <a href="#pricing">$3 EcoCash</a>
          <Link href="/mashtech">Mashtech</Link>
          <Link href="/trial">Trial codes</Link>
          <Link className={styles.navCta} href="/register">
            Register shop
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
            Register. Get your QR. Mashtech posts the glad reviews.
          </h1>
          <p className={styles.heroSupport}>
            Small shops in Zimbabwe: $3 / month on EcoCash. Automatic customer
            follow-ups. Bad reviews stay private.
          </p>
          <div className={styles.ctaRow}>
            <Link className={styles.btnPrimary} href="/register?code=MASHTECH14">
              Start free trial
            </Link>
            <Link className={styles.btnGhost} href="/trial">
              Trial codes & links
            </Link>
          </div>
        </div>
      </section>

      <section className={styles.section} id="how">
        <div className={styles.sectionNarrow}>
          <div className={styles.sectionHead}>
            <h2>Your link and QR become the review desk.</h2>
            <p>
              Register once. Print the QR. GladGate checks in with customers and
              Mashtech shares the happy ones on social — tagging your page.
            </p>
          </div>
          <div className={styles.problem}>
            <blockquote className={styles.quote}>
              Unhappy clients write one-star essays at midnight. GladGate asks
              registered customers automatically — and only the glad voices go
              public through Mashtech.
              <span>Powered by Mashtech · EcoCash $3 / month after trial.</span>
            </blockquote>
            <div className={styles.flow}>
              <div className={styles.flowStep}>
                <strong>1. Register your company</strong>
                <p>
                  Get a unique review link and QR code for your counter, till, or
                  WhatsApp status.
                </p>
              </div>
              <div className={styles.flowStep}>
                <strong>2. Automatic checks & follow-ups</strong>
                <p>
                  Every registered customer gets scheduled WhatsApp/SMS pulses.
                  No more hoping people remember to review.
                </p>
              </div>
              <div className={styles.flowStep}>
                <strong>3. Mashtech posts the glad ones</strong>
                <p>
                  4–5★ clean reviews are queued for Mashtech to post, tagging
                  your Facebook page. Low scores stay private.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className={styles.section} id="businesses">
        <div className={styles.sectionNarrow}>
          <div className={styles.sectionHead}>
            <h2>Built for everyday Zimbabwe shops.</h2>
            <p>
              Restaurants, workshops, salons, pharmacies, lodges, clinics,
              hardware counters, and car washes.
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
            <h2>$3 on EcoCash. Trial codes before launch.</h2>
            <p>
              Launch price for small companies. Use a trial code now — pay EcoCash
              when you go live.
            </p>
          </div>
          <div className={styles.pricingGrid}>
            {PLANS.map((plan) => (
              <article
                key={plan.id}
                className={`${styles.plan} ${
                  plan.highlighted ? styles.planFeatured : ""
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
                  {plan.currencyLabel} · {plan.locations}
                </p>
                <ul>
                  {plan.features.map((feature) => (
                    <li key={feature}>{feature}</li>
                  ))}
                </ul>
                <Link
                  className={
                    plan.highlighted ? styles.btnPrimary : styles.btnDark
                  }
                  href={
                    plan.id === "ecocash_starter"
                      ? "/register?code=MASHTECH14"
                      : "/register"
                  }
                >
                  Register shop
                </Link>
              </article>
            ))}
          </div>

          <div className={styles.sectionHead} style={{ marginTop: "2.5rem" }}>
            <h2>Pre-launch trial codes</h2>
            <p>Share these links with shops before billing goes live.</p>
          </div>
          <div className={styles.flow}>
            {TRIAL_OFFERS.map((trial) => (
              <div key={trial.code} className={styles.flowStep}>
                <strong>
                  {trial.code} · {trial.days} days
                </strong>
                <p>
                  {trial.description}{" "}
                  <Link href={trial.registerPath}>{trial.registerPath}</Link>
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className={styles.footer}>
        <div>
          <strong>GladGate by Mashtech</strong>
          <div>Ask happy. Hold hurt. Post glad reviews.</div>
        </div>
        <div>
          <Link href="/mashtech">Mashtech dashboard →</Link>
          {" · "}
          <Link href="/register">Register →</Link>
          {" · "}
          <Link href="/b/amanzi-grill/dashboard">Sample shop →</Link>
        </div>
      </footer>
    </div>
  );
}
