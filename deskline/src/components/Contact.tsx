import { useState, type FormEvent } from 'react'

export function Contact() {
  const [sent, setSent] = useState(false)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSent(true)
  }

  return (
    <div className="container">
      <section className="cta-band" id="contact">
        <p className="eyebrow">Ready when you close</p>
        <h2>Stop losing the calls that never call back.</h2>
        <p>
          Tell us your vertical and average after-hours volume. We’ll configure
          Deskline scripts, calendar rules, and a go-live plan for your team.
        </p>

        {!sent ? (
          <form className="lead-form" onSubmit={handleSubmit} style={{ maxWidth: 420 }}>
            <div className="field">
              <label htmlFor="biz">Business name</label>
              <input id="biz" name="business" required placeholder="Brightside Dental" />
            </div>
            <div className="field">
              <label htmlFor="email">Work email</label>
              <input
                id="email"
                name="email"
                type="email"
                required
                placeholder="you@practice.com"
              />
            </div>
            <div className="field">
              <label htmlFor="vertical">Vertical</label>
              <select id="vertical" name="vertical" defaultValue="dental">
                <option value="dental">Dental surgery</option>
                <option value="plumber">Plumbing</option>
                <option value="medspa">Med spa</option>
              </select>
            </div>
            <button className="btn btn-primary" type="submit">
              Request setup call
            </button>
          </form>
        ) : (
          <div className="success-note">
            Thanks — a Deskline specialist will reach out within one business day
            to map your hours, scripts, and calendar.
          </div>
        )}
      </section>
    </div>
  )
}
