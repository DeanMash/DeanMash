export function Footer() {
  return (
    <footer className="site-footer">
      <div className="container footer-row">
        <div className="brand">
          <span className="brand-dot" aria-hidden="true" />
          <span className="brand-mark">Deskline</span>
        </div>
        <p>After-hours AI receptionist for dental, plumbing, and med spa teams.</p>
        <p>© {new Date().getFullYear()} Deskline</p>
      </div>
    </footer>
  )
}
