export function Problem() {
  return (
    <>
      <div className="stat-strip">
        <div className="container stat-grid">
          <div className="stat">
            <strong>85%</strong>
            <span>of missed after-hours callers never ring back</span>
          </div>
          <div className="stat">
            <strong>5pm</strong>
            <span>is when high-intent enquiries still keep coming</span>
          </div>
          <div className="stat">
            <strong>Next day</strong>
            <span>working-hours appointments booked while you sleep</span>
          </div>
        </div>
      </div>

      <section className="section" id="problem">
        <div className="container problem-grid">
          <div>
            <div className="section-head" style={{ marginBottom: 0 }}>
              <p className="eyebrow">The leak in your diary</p>
              <h2>Closing time should not close the business.</h2>
              <p>
                Pain calls, burst pipes, and treatment enquiries do not wait for
                your front desk. If nobody answers, most people move on — to a
                competitor who picks up.
              </p>
              <p style={{ marginTop: '1rem' }}>
                Deskline is the after-hours AI receptionist built for dental
                surgeries, plumbers, and med spas: it answers every ring, asks
                the right questions, and books the best available working-hours
                slot.
              </p>
            </div>
          </div>
          <div className="panel loss-panel">
            <div className="big">85%</div>
            <p>of those late calls are gone forever if you only leave a voicemail.</p>
          </div>
        </div>
      </section>
    </>
  )
}
