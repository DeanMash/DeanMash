import { plans } from '../data/pricing'

function formatPrice(value: number) {
  return value.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  })
}

export function Pricing() {
  return (
    <section className="section" id="pricing">
      <div className="container">
        <div className="section-head">
          <p className="eyebrow">Pricing</p>
          <h2>One predictable monthly retainer. No per-minute surprises.</h2>
          <p>
            Deskline is priced for practices that already pay for empty chairs and
            missed jobs — from $1,000 to $3,000 per month.
          </p>
        </div>
        <div className="pricing-grid">
          {plans.map((plan) => (
            <article
              key={plan.id}
              className={`price-card${plan.highlighted ? ' featured' : ''}`}
            >
              <div>
                <p className="eyebrow" style={{ marginBottom: '0.6rem' }}>
                  {plan.name}
                </p>
                <div className="amount">
                  {formatPrice(plan.price)}
                  <span> / month</span>
                </div>
              </div>
              <p style={{ color: 'var(--sand-dim)' }}>{plan.blurb}</p>
              <p>
                <strong style={{ color: 'var(--sand)' }}>Best for:</strong>{' '}
                <span style={{ color: 'var(--sand-dim)' }}>{plan.bestFor}</span>
              </p>
              <ul>
                {plan.features.map((feature) => (
                  <li key={feature}>{feature}</li>
                ))}
              </ul>
              <a className="btn btn-primary" href="#contact">
                Start with {plan.name}
              </a>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
