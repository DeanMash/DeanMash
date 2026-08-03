import { industries, type IndustryId } from '../data/industries'

type Props = {
  selected: IndustryId
  onSelect: (id: IndustryId) => void
}

export function Industries({ selected, onSelect }: Props) {
  return (
    <section className="section" id="industries">
      <div className="container">
        <div className="section-head">
          <p className="eyebrow">Built for service businesses</p>
          <h2>Scripts that sound like your front desk — not a generic bot.</h2>
          <p>
            Pick a vertical to load the right qualification flow in the live demo
            below.
          </p>
        </div>
        <div className="industry-grid">
          {industries.map((industry) => (
            <button
              key={industry.id}
              type="button"
              className={`industry-tile${selected === industry.id ? ' active' : ''}`}
              onClick={() => {
                onSelect(industry.id)
                document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' })
              }}
            >
              <img src={industry.image} alt={industry.imageAlt} />
              <div className="industry-copy">
                <h3>{industry.name}</h3>
                <p>{industry.headline}</p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </section>
  )
}
