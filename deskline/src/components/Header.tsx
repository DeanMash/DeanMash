export function Header() {
  return (
    <header className="site-header">
      <div className="container nav">
        <a className="brand" href="#top" aria-label="Deskline home">
          <span className="brand-dot" aria-hidden="true" />
          <span className="brand-mark">Deskline</span>
        </a>
        <nav className="nav-links" aria-label="Primary">
          <a href="#how">How it works</a>
          <a href="#industries">Industries</a>
          <a href="#demo">Live demo</a>
          <a href="#pricing">Pricing</a>
        </nav>
        <a className="btn btn-primary" href="#demo">
          Try the demo
        </a>
      </div>
    </header>
  )
}
