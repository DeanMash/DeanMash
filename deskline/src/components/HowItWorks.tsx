const steps = [
  {
    num: '01',
    title: 'Answer every ring',
    body: 'Calls that hit after closing are answered in your brand voice — no hold music, no “leave a message.”',
  },
  {
    num: '02',
    title: 'Qualify the lead',
    body: 'Deskline asks industry-specific questions: urgency, service type, access, patient status, or consult readiness.',
  },
  {
    num: '03',
    title: 'Book the diary',
    body: 'It offers the following working day — or the soonest best slot — then confirms by SMS and syncs your calendar.',
  },
]

export function HowItWorks() {
  return (
    <section className="section" id="how">
      <div className="container">
        <div className="section-head">
          <p className="eyebrow">How Deskline works</p>
          <h2>From missed call to held appointment in one conversation.</h2>
          <p>
            No new software for your team to babysit overnight. Deskline runs the
            intake, scores the lead, and leaves you a clean booking for the morning.
          </p>
        </div>
        <div className="steps">
          {steps.map((step) => (
            <article className="step" key={step.num}>
              <div className="num">{step.num}</div>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
