const nav = document.getElementById("nav");

window.addEventListener("scroll", () => {
  nav.classList.toggle("is-scrolled", window.scrollY > 12);
});

const revealEls = document.querySelectorAll(".reveal");
const io = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        io.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.18 }
);
revealEls.forEach((el) => io.observe(el));

async function loadVerticals() {
  const res = await fetch("/api/verticals");
  const data = await res.json();
  const grid = document.getElementById("verticals");
  const select = document.getElementById("lead-vertical");
  grid.innerHTML = data
    .map(
      (v) => `
      <article>
        <h3>${v.label}</h3>
        <p>${v.why}</p>
      </article>`
    )
    .join("");
  select.innerHTML = data
    .map((v) => `<option value="${v.key}">${v.label}</option>`)
    .join("");
}

async function loadPlans() {
  const res = await fetch("/api/plans");
  const data = await res.json();
  const root = document.getElementById("plans");
  root.innerHTML = data
    .map((p, i) => {
      const featured = i === 1 ? "featured" : "";
      const btn = i === 1 ? "btn-sun" : "btn-primary";
      return `
      <article class="plan ${featured}">
        <h3>${p.name}</h3>
        <div class="price">$${p.price_usd.toLocaleString()}<small>/mo</small></div>
        <p class="muted">${p.tagline}</p>
        <p class="muted"><strong>${p.clients}</strong><br />${p.best_for}</p>
        <ul>${p.features.map((f) => `<li>${f}</li>`).join("")}</ul>
        <a class="btn ${btn}" href="#book">Choose ${p.name}</a>
      </article>`;
    })
    .join("");
}

document.getElementById("lead-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const note = document.getElementById("lead-note");
  const payload = Object.fromEntries(new FormData(form).entries());
  note.textContent = "Sending…";
  try {
    const res = await fetch("/api/leads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error("failed");
    note.textContent = data.next || "Received — we’ll WhatsApp you soon.";
    form.reset();
  } catch {
    note.textContent = "Could not send just now. WhatsApp us directly instead.";
  }
});

loadVerticals();
loadPlans();
