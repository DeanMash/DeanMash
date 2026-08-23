(() => {
  const tokenInput = document.getElementById("token");
  const bizName = document.getElementById("biz-name");
  const bizMeta = document.getElementById("biz-meta");
  const bizSwitch = document.getElementById("biz-switch");
  const statsEl = document.getElementById("stats");
  const prospectsBody = document.getElementById("prospects-body");
  const messagesEl = document.getElementById("messages");
  const eventsEl = document.getElementById("events");
  const previewEl = document.getElementById("preview");
  const addForm = document.getElementById("add-prospect");
  const startTip = document.getElementById("start-tip");
  const startSteps = document.querySelectorAll(".start-steps li");
  const channelSelect = document.getElementById("channel-select");
  const autoRunSelect = document.getElementById("auto-run-select");

  const params = new URLSearchParams(window.location.search);
  const state = {
    businessId: params.get("business_id") || localStorage.getItem("openpipe_biz") || "",
    done: {
      1: localStorage.getItem("openpipe_step1") === "1",
      2: localStorage.getItem("openpipe_step2") === "1",
      3: localStorage.getItem("openpipe_step3") === "1",
    },
  };

  const savedToken = localStorage.getItem("openpipe_token");
  if (savedToken) tokenInput.value = savedToken;

  tokenInput.addEventListener("change", () => {
    localStorage.setItem("openpipe_token", tokenInput.value.trim());
  });

  function headers() {
    const h = { "Content-Type": "application/json" };
    const t = tokenInput.value.trim();
    if (t) h["X-Openpipe-Token"] = t;
    return h;
  }

  function withBiz(path) {
    if (!state.businessId) return path;
    const sep = path.includes("?") ? "&" : "?";
    return `${path}${sep}business_id=${encodeURIComponent(state.businessId)}`;
  }

  async function api(path, opts = {}) {
    const res = await fetch(withBiz(path), {
      ...opts,
      headers: { ...headers(), ...(opts.headers || {}) },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || res.statusText);
    }
    return res.json();
  }

  function markStep(n) {
    state.done[n] = true;
    localStorage.setItem(`openpipe_step${n}`, "1");
    paintSteps();
  }

  function paintSteps() {
    startSteps.forEach((li) => {
      const n = Number(li.dataset.step);
      li.classList.toggle("done", Boolean(state.done[n]));
    });
  }

  function statCard(label, value) {
    return `<div class="stat"><div class="label">${label}</div><div class="value">${value}</div></div>`;
  }

  async function preview(prospectId, day = 0, channel = "email") {
    const data = await api(
      `/api/preview?prospect_id=${encodeURIComponent(prospectId)}&day=${day}&channel=${encodeURIComponent(channel)}`
    );
    previewEl.innerHTML = `
      <h3>${data.channel === "whatsapp" ? "WhatsApp" : "Email"} preview · Day ${data.day}</h3>
      <p class="msg-meta">To ${data.to}</p>
      <p><strong>${data.subject}</strong></p>
      <pre>${data.body}</pre>
      <div class="actions" style="margin-top:0.5rem">
        <button type="button" data-day="0" data-ch="email">Email D0</button>
        <button type="button" data-day="3" data-ch="email">Email D3</button>
        <button type="button" data-day="7" data-ch="email">Email D7</button>
        <button type="button" data-day="0" data-ch="whatsapp">WA D0</button>
        <button type="button" data-day="3" data-ch="whatsapp">WA D3</button>
        <button type="button" data-day="7" data-ch="whatsapp">WA D7</button>
      </div>`;
    previewEl.querySelectorAll("button[data-day]").forEach((btn) => {
      btn.addEventListener("click", () =>
        preview(prospectId, Number(btn.dataset.day), btn.dataset.ch)
      );
    });
    markStep(2);
  }

  async function loadBusinesses() {
    const list = await api("/api/businesses");
    if (!state.businessId || !list.some((b) => b.id === state.businessId)) {
      state.businessId = list[0]?.id || "";
      localStorage.setItem("openpipe_biz", state.businessId);
    }
    bizSwitch.innerHTML = list
      .map(
        (b) =>
          `<option value="${b.id}" ${b.id === state.businessId ? "selected" : ""}>${b.name} · ${b.vertical}</option>`
      )
      .join("");
    return list;
  }

  async function refresh() {
    await loadBusinesses();
    const [biz, stats, prospects, messages, events] = await Promise.all([
      api("/api/business"),
      api("/api/stats"),
      api("/api/prospects"),
      api("/api/messages"),
      api("/api/events"),
    ]);

    bizName.textContent = biz.name;
    bizMeta.textContent = `${biz.vertical} · ${biz.city} · ${biz.sender_name} · ${biz.plan} · channels: ${biz.channels} · niche: ${biz.niche || "—"}`;
    startTip.textContent =
      biz.start_tip ||
      biz.blurb ||
      "Find prospects, preview email/WhatsApp, then send.";
    channelSelect.value = biz.channels || "both";
    autoRunSelect.value = String(biz.auto_run ?? 1);

    statsEl.innerHTML = [
      statCard("Prospects", stats.prospects),
      statCard("Sequenced", stats.sequenced),
      statCard("Replied", stats.replied),
      statCard("Meetings", stats.meetings),
      statCard("Sent", stats.messages_sent),
      statCard("Email", stats.email_sent ?? 0),
      statCard("WhatsApp", stats.whatsapp_sent ?? 0),
      statCard("Queued", stats.messages_queued),
      statCard("Reply %", stats.reply_rate),
    ].join("");

    prospectsBody.innerHTML = prospects
      .map(
        (p) => `
      <tr>
        <td>
          <strong>${p.full_name}</strong><br />
          <span class="msg-meta">${p.title || "—"} · ${p.email || "no email"}${p.phone ? " · " + p.phone : ""}</span>
        </td>
        <td>${p.company}<br /><span class="msg-meta">${p.trigger || ""}</span></td>
        <td><span class="status ${p.status}">${p.status}</span></td>
        <td>
          <div class="actions">
            <button type="button" data-preview="${p.id}">Preview</button>
            <button type="button" data-replied="${p.id}">Replied</button>
            <button type="button" data-meeting="${p.id}">Meeting</button>
          </div>
        </td>
      </tr>`
      )
      .join("");

    prospectsBody.querySelectorAll("[data-preview]").forEach((btn) => {
      btn.addEventListener("click", () => {
        preview(btn.dataset.preview, 0, "email")
          .then(() => previewEl.scrollIntoView({ behavior: "smooth", block: "nearest" }))
          .catch((err) => alert(String(err.message || err)));
      });
    });
    prospectsBody.querySelectorAll("[data-replied]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        await api("/api/replied", {
          method: "POST",
          body: JSON.stringify({ prospect_id: btn.dataset.replied }),
        });
        await refresh();
      });
    });
    prospectsBody.querySelectorAll("[data-meeting]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        await api("/api/meeting", {
          method: "POST",
          body: JSON.stringify({ prospect_id: btn.dataset.meeting }),
        });
        await refresh();
      });
    });

    messagesEl.innerHTML = messages.length
      ? messages
          .slice(0, 50)
          .map(
            (m) => `
        <div class="msg-item">
          <strong><span class="channel-pill ${m.channel}">${m.channel}</span> Day ${m.day} · ${m.status}</strong>
          <div>${m.subject}</div>
          <div class="msg-meta">${m.scheduled_for}${m.sent_at ? " · sent " + m.sent_at : ""}</div>
        </div>`
          )
          .join("")
      : "<p class='tiny'>No messages yet.</p>";

    eventsEl.innerHTML = events.length
      ? events
          .slice(0, 25)
          .map(
            (e) => `
        <div class="event-item">
          <strong>${e.kind}</strong>
          <div class="event-meta">${e.created_at}</div>
          <div class="msg-meta">${JSON.stringify(e.payload)}</div>
        </div>`
          )
          .join("")
      : "<p class='tiny'>No activity yet.</p>";

    paintSteps();
  }

  bizSwitch.addEventListener("change", async () => {
    state.businessId = bizSwitch.value;
    localStorage.setItem("openpipe_biz", state.businessId);
    state.done = { 1: false, 2: false, 3: false };
    localStorage.removeItem("openpipe_step1");
    localStorage.removeItem("openpipe_step2");
    localStorage.removeItem("openpipe_step3");
    previewEl.innerHTML =
      "<h3>Message preview</h3><p>Select Preview on a prospect to see Day 0 / 3 / 7 email or WhatsApp copy.</p>";
    await refresh();
  });

  document.getElementById("btn-save-settings").addEventListener("click", async () => {
    try {
      await api("/api/business", {
        method: "PATCH",
        body: JSON.stringify({
          channels: channelSelect.value,
          auto_run: Number(autoRunSelect.value),
        }),
      });
      await refresh();
      alert("Settings saved — plan rebuilt for channel mix.");
    } catch (err) {
      alert(String(err.message || err));
    }
  });

  document.getElementById("btn-refresh").addEventListener("click", () => refresh().catch(alert));
  document.getElementById("btn-plan").addEventListener("click", async () => {
    await api("/api/plan", { method: "POST", body: "{}" });
    await refresh();
  });
  document.getElementById("btn-run").addEventListener("click", async () => {
    const result = await api("/api/run", { method: "POST", body: "{}" });
    markStep(3);
    const ch = result.by_channel || {};
    alert(
      `Sent ${result.sent} (email ${ch.email || 0} · WhatsApp ${ch.whatsapp || 0}) · failed ${result.failed}`
    );
    await refresh();
  });
  document.getElementById("btn-discover").addEventListener("click", async () => {
    const result = await api("/api/discover", {
      method: "POST",
      body: JSON.stringify({ limit: 6 }),
    });
    markStep(1);
    alert(`Added ${result.added} prospects · planned ${result.messages_planned} messages`);
    await refresh();
  });

  addForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(addForm).entries());
    await api("/api/prospects", { method: "POST", body: JSON.stringify(data) });
    addForm.reset();
    markStep(1);
    await refresh();
  });

  refresh().catch((err) => {
    bizName.textContent = "Could not load dashboard";
    bizMeta.textContent = String(err.message || err);
  });
})();
