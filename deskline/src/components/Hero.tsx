export function Hero() {
  return (
    <section className="hero" id="top" aria-label="Deskline hero">
      <div className="hero-media" aria-hidden="true">
        <img
          src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=2000&q=80"
          alt=""
        />
      </div>
      <div className="hero-shade" aria-hidden="true" />
      <div className="hero-copy">
        <p className="hero-brand">
          Desk<span>line</span>
        </p>
        <h1>Every after-hours call answered, qualified, and booked.</h1>
        <p className="hero-support">
          When your dental surgery, plumbing van, or med spa closes at 5, Deskline
          keeps the front desk open — so 85% of those missed callers become
          tomorrow’s appointments.
        </p>
        <div className="hero-actions">
          <a className="btn btn-primary" href="#demo">
            Book a next-day slot — demo
          </a>
          <a className="btn btn-ghost" href="#pricing">
            View plans from $1,000/mo
          </a>
        </div>
      </div>
    </section>
  )
}
