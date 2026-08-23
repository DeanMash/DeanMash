(() => {
  const verticalEl = document.getElementById("reg-vertical");
  const form = document.getElementById("register-form");
  const note = document.getElementById("reg-note");
  const tokenBox = document.getElementById("token-box");
  const tokenEl = document.getElementById("access-token");
  const openDash = document.getElementById("open-dash");
  const copyBtn = document.getElementById("copy-token");
  const loginForm = document.getElementById("login-form");
  const loginNote = document.getElementById("login-note");

  fetch("/api/verticals")
    .then((r) => r.json())
    .then((verticals) => {
      verticalEl.innerHTML = verticals
        .map((v) => `<option value="${v.key}">${v.label}</option>`)
        .join("");
    })
    .catch(() => {
      verticalEl.innerHTML =
        '<option value="insurance">Insurance brokers</option><option value="advisor">Financial advisors</option><option value="b2b">B2B services</option>';
    });

  function saveSession(token, businessId) {
    localStorage.setItem("openpipe_token", token);
    localStorage.setItem("openpipe_biz", businessId);
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    note.textContent = "Creating your organisation…";
    const data = Object.fromEntries(new FormData(form).entries());
    data.seed_prospects = true;
    try {
      const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || "Registration failed");
      const token = json.access_token;
      const biz = json.business;
      saveSession(token, biz.id);
      tokenEl.textContent = token;
      openDash.href = `/dashboard?business_id=${encodeURIComponent(biz.id)}`;
      tokenBox.hidden = false;
      note.textContent = `Seeded ${json.seeded.added} prospects · ${json.seeded.messages_planned} messages queued.`;
      tokenBox.scrollIntoView({ behavior: "smooth" });
    } catch (err) {
      note.textContent = String(err.message || err);
    }
  });

  copyBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(tokenEl.textContent);
      copyBtn.textContent = "Copied";
    } catch {
      copyBtn.textContent = "Select & copy manually";
    }
  });

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginNote.textContent = "Checking…";
    const data = Object.fromEntries(new FormData(loginForm).entries());
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || "Login failed");
      saveSession(json.access_token, json.business.id);
      window.location.href = `/dashboard?business_id=${encodeURIComponent(json.business.id)}`;
    } catch (err) {
      loginNote.textContent = String(err.message || err);
    }
  });
})();
