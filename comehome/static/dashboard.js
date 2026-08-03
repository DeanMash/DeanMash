const tokenInput = document.getElementById("token");
tokenInput.value = localStorage.getItem("comehome_token") || "";
tokenInput.addEventListener("change", () => {
  localStorage.setItem("comehome_token", tokenInput.value.trim());
});

function headers() {
  const h = { "Content-Type": "application/json" };
  const token = tokenInput.value.trim();
  if (token) h["X-Comehome-Token"] = token;
  return h;
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    ...options,
    headers: { ...headers(), ...(options.headers || {}) },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

function moneyPlan(plan) {
  const map = { studio: "$800", practice: "$1,400", chain: "$2,000" };
  return map[plan] || plan;
}

async function loadAll() {
  const [biz, stats, clients, messages, events] = await Promise.all([
    api("/api/business"),
    api("/api/stats"),
    api("/api/clients"),
    api("/api/messages"),
    api("/api/events"),
  ]);

  document.getElementById("biz-name").textContent = biz.name;
  document.getElementById("biz-meta").textContent =
    `${biz.city} · ${biz.vertical} · Plan ${biz.plan} (${moneyPlan(biz.plan)}/mo) · WhatsApp ${biz.whatsapp_from}`;

  document.getElementById("stats").innerHTML = [
    ["Clients", stats.clients],
    ["Lapsing", stats.lapsing],
    ["Recovered", stats.recovered],
    ["At 30 days", stats.at_30],
    ["At 60 days", stats.at_60],
    ["At 90 days", stats.at_90],
  ]
    .map(
      ([label, value]) =>
        `<div class="stat"><b>${value}</b><span>${label}</span></div>`
    )
    .join("");

  document.getElementById("clients-body").innerHTML = clients
    .map(
      (c) => `
      <tr>
        <td>
          <strong>${c.full_name}</strong><br />
          <span class="tiny">${c.phone}</span>
        </td>
        <td>${c.days_since_visit}</td>
        <td><span class="status ${c.status}">${c.status.replace("_", " ")}</span></td>
        <td>
          <button class="btn secondary" data-preview="${c.id}" type="button">Preview</button>
          ${
            c.status !== "recovered"
              ? `<button class="btn sun" data-recover="${c.id}" type="button">Recovered</button>`
              : ""
          }
        </td>
      </tr>`
    )
    .join("");

  document.getElementById("messages").innerHTML = messages
    .slice(0, 12)
    .map((m) => {
      const client = clients.find((c) => c.id === m.client_id);
      return `
      <div class="msg">
        <strong>Day ${m.day} · ${m.status} · ${client ? client.full_name : m.client_id}</strong>
        <p>${m.subject}<br />${m.body.slice(0, 140)}${m.body.length > 140 ? "…" : ""}</p>
        <p class="tiny">Scheduled ${new Date(m.scheduled_for).toLocaleString()}</p>
      </div>`;
    })
    .join("") || "<p class='tiny'>No messages yet. Click Rebuild plan.</p>";

  document.getElementById("events").innerHTML = events
    .slice(0, 10)
    .map((e) => {
      const payload = e.payload || {};
      const detail =
        e.kind === "message_sent"
          ? `${payload.client_name} · day ${payload.day} via ${payload.channel}`
          : e.kind === "lead"
            ? `${payload.name} · ${payload.business} · ${payload.phone}`
            : e.kind === "recovered"
              ? payload.client_name
              : JSON.stringify(payload).slice(0, 120);
      return `<div class="event"><strong>${e.kind}</strong><p>${detail}</p></div>`;
    })
    .join("") || "<p class='tiny'>No activity yet.</p>";
}

document.getElementById("clients-body").addEventListener("click", async (e) => {
  const previewId = e.target.getAttribute("data-preview");
  const recoverId = e.target.getAttribute("data-recover");
  if (previewId) {
    const day = prompt("Preview which day? 30, 60, or 90", "30") || "30";
    const data = await api(`/api/preview?client_id=${previewId}&day=${day}`);
    document.getElementById("preview").innerHTML = `
      <h3>Day ${data.day} · ${data.channel} → ${data.to}</h3>
      <p><strong>${data.subject}</strong></p>
      <p>${data.body}</p>`;
  }
  if (recoverId) {
    await api("/api/recover", {
      method: "POST",
      body: JSON.stringify({ client_id: recoverId }),
    });
    await loadAll();
  }
});

document.getElementById("add-client").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const payload = Object.fromEntries(new FormData(form).entries());
  await api("/api/clients", { method: "POST", body: JSON.stringify(payload) });
  form.reset();
  await loadAll();
});

document.getElementById("btn-refresh").addEventListener("click", () => loadAll());
document.getElementById("btn-plan").addEventListener("click", async () => {
  await api("/api/plan", { method: "POST" });
  await loadAll();
});
document.getElementById("btn-run").addEventListener("click", async () => {
  const result = await api("/api/run", { method: "POST" });
  alert(`Sent ${result.sent}, failed ${result.failed}, checked ${result.checked}`);
  await loadAll();
});

loadAll().catch((err) => {
  document.getElementById("biz-name").textContent = "Could not load dashboard";
  document.getElementById("biz-meta").textContent = err.message;
});
