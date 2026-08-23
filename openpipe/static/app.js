(() => {
  const nav = document.getElementById("nav");
  const verticalsEl = document.getElementById("verticals");
  const coreIcpsEl = document.getElementById("core-icps");
  const plansEl = document.getElementById("plans");
  const leadVertical = document.getElementById("lead-vertical");
  const leadForm = document.getElementById("lead-form");
  const leadNote = document.getElementById("lead-note");
  const sampleTabs = document.getElementById("sample-tabs");
  const mailStack = document.getElementById("mail-stack");

  let samples = [];
  let activeSample = "insurance";

  window.addEventListener("scroll", () => {
    nav.classList.toggle("is-scrolled", window.scrollY > 12);
  });

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) e.target.classList.add("is-visible");
      });
    },
    { threshold: 0.15 }
  );
  document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

  function excerpt(body) {
    const line = body
      .split("\n")
      .map((s) => s.trim())
      .find((s) => s && !s.startsWith("Hi ") && !s.startsWith("I'm ") && s.length > 20);
    if (!line) return body.slice(0, 140) + "…";
    return line.length > 160 ? line.slice(0, 157) + "…" : line;
  }

  function renderSamples() {
    const sample = samples.find((s) => s.vertical === activeSample) || samples[0];
    if (!sample) return;

    sampleTabs.innerHTML = samples
      .map(
        (s) => `
      <button type="button" class="sample-tab${s.vertical === activeSample ? " is-active" : ""}" data-v="${s.vertical}">
        ${s.label}
      </button>`
      )
      .join("");

    sampleTabs.querySelectorAll(".sample-tab").forEach((btn) => {
      btn.addEventListener("click", () => {
        activeSample = btn.dataset.v;
        renderSamples();
      });
    });

    const dayLabel = { 0: "First touch", 3: "Value bump", 7: "Soft close" };
    mailStack.innerHTML = sample.days
      .map(
        (d) => `
      <article class="mail-card">
        <header>
          <span>Day ${d.day} · ${dayLabel[d.day] || "Follow-up"}</span>
          <strong>${d.subject}</strong>
        </header>
        <p>${excerpt(d.body)}</p>
        ${
          d.whatsapp
            ? `<p class="mail-meta">WhatsApp: ${excerpt(d.whatsapp)}</p>`
            : ""
        }
        <p class="mail-meta">${sample.prospect} · ${sample.company}</p>
      </article>`
      )
      .join("");
  }

  async function load() {
    const [verticals, plans, sampleData, starters] = await Promise.all([
      fetch("/api/verticals").then((r) => r.json()),
      fetch("/api/plans").then((r) => r.json()),
      fetch("/api/samples").then((r) => r.json()),
      fetch("/api/starters").then((r) => r.json()),
    ]);

    samples = sampleData;
    renderSamples();

    const coreLabels = {
      insurance: "Insurance brokers",
      advisor: "Financial advisors",
      b2b: "B2B services",
    };
    coreIcpsEl.innerHTML = starters
      .map(
        (s) => `
      <article class="core-icp">
        <h3>${coreLabels[s.vertical] || s.name}</h3>
        <p>${s.blurb}</p>
        <p class="core-tip">${s.start_tip}</p>
      </article>`
      )
      .join("");

    verticalsEl.innerHTML = verticals
      .map(
        (v) => `
      <article class="vertical-item reveal">
        <h3>${v.label}</h3>
        <p>${v.why}</p>
      </article>`
      )
      .join("");
    verticalsEl.querySelectorAll(".reveal").forEach((el) => io.observe(el));

    leadVertical.innerHTML = verticals
      .map((v) => `<option value="${v.key}">${v.label}</option>`)
      .join("");

    plansEl.innerHTML = plans
      .map((p) => {
        const featured = p.key === "pipeline" ? " featured" : "";
        const features = p.features.map((f) => `<li>${f}</li>`).join("");
        return `
        <article class="plan${featured} reveal">
          <h3>${p.name}</h3>
          <p class="price">$${p.price_usd.toLocaleString()}<span>/mo</span></p>
          <p class="tagline">${p.tagline}</p>
          <p class="best">${p.prospects}</p>
          <ul>${features}</ul>
          <p class="best">${p.best_for}</p>
          <a class="btn btn-primary" href="#book" style="width:100%;margin-top:0.5rem">Choose ${p.name}</a>
        </article>`;
      })
      .join("");
    plansEl.querySelectorAll(".reveal").forEach((el) => io.observe(el));
  }

  leadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    leadNote.textContent = "Sending…";
    const data = Object.fromEntries(new FormData(leadForm).entries());
    try {
      const res = await fetch("/api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || "Failed");
      leadNote.textContent = json.next || "Received — we'll be in touch.";
      leadForm.reset();
      leadForm.querySelector('[name="city"]').value = "Harare";
      leadForm.querySelector('[name="plan"]').value = "pipeline";
    } catch (err) {
      leadNote.textContent = "Could not send — try again shortly.";
    }
  });

  load().catch(() => {
    verticalsEl.innerHTML = "<p>Could not load verticals.</p>";
    mailStack.innerHTML = "<p>Could not load sample emails.</p>";
  });
})();
