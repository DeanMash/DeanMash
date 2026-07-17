const tokenInput = document.getElementById("tokenInput");
const instagramInput = document.getElementById("instagramInput");
const refreshBtn = document.getElementById("refreshBtn");
const statusEl = document.getElementById("status");
const accountPanel = document.getElementById("accountPanel");
const accountLine = document.getElementById("accountLine");
const newsPanel = document.getElementById("newsPanel");
const newsSummary = document.getElementById("newsSummary");
const newsList = document.getElementById("newsList");
const instagramPanel = document.getElementById("instagramPanel");
const instagramSummary = document.getElementById("instagramSummary");
const instagramList = document.getElementById("instagramList");
const suggestionsPanel = document.getElementById("suggestionsPanel");
const suggestionsList = document.getElementById("suggestionsList");

const TOKEN_KEY = "deriv_advisor_dashboard_token";

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function savedToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

function persistToken(value) {
  if (value) {
    localStorage.setItem(TOKEN_KEY, value);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

function renderReport(data) {
  accountPanel.hidden = false;
  newsPanel.hidden = false;
  instagramPanel.hidden = false;
  suggestionsPanel.hidden = false;

  accountLine.textContent = `${data.account.loginid} · ${data.account.type} · ${data.account.balance.toFixed(2)} ${data.account.currency}`;

  newsSummary.textContent = `${data.news.summary} (${data.news.headline_count} headlines, score ${data.news.score})`;
  newsList.innerHTML = "";
  for (const title of data.news.sample_titles || []) {
    const li = document.createElement("li");
    li.textContent = title;
    newsList.appendChild(li);
  }

  const ig = data.instagram || {};
  instagramSummary.textContent = `${ig.summary || "No Instagram links provided."} (${ig.fetched_count || 0}/${ig.post_count || 0} captions loaded)`;
  instagramList.innerHTML = "";
  const captions = ig.sample_captions || [];
  if (!captions.length && (ig.posts || []).length) {
    for (const post of ig.posts) {
      const li = document.createElement("li");
      li.textContent = post.fetched ? post.caption || post.title : `${post.url} — ${post.note}`;
      instagramList.appendChild(li);
    }
  } else {
    for (const caption of captions) {
      const li = document.createElement("li");
      li.textContent = caption;
      instagramList.appendChild(li);
    }
  }

  suggestionsList.innerHTML = "";
  if (!data.suggestions.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = `No ideas met the ${data.min_confidence}% confidence threshold right now.`;
    suggestionsList.appendChild(empty);
    return;
  }

  data.suggestions.forEach((idea, index) => {
    const card = document.createElement("article");
    card.className = "idea";
    card.style.animationDelay = `${index * 0.05}s`;

    const direction = String(idea.direction || "").toLowerCase();
    card.innerHTML = `
      <div class="idea-top">
        <div>
          <div class="idea-symbol">${idea.symbol}</div>
          <div class="idea-meta">Last ${idea.last_price}</div>
        </div>
        <div>
          <span class="badge ${direction}">${idea.direction}</span>
          <div class="confidence">${idea.confidence.toFixed(1)}% confidence</div>
        </div>
      </div>
      <ul class="reasons"></ul>
    `;

    const reasons = card.querySelector(".reasons");
    for (const reason of idea.reasons || []) {
      const li = document.createElement("li");
      li.textContent = reason;
      reasons.appendChild(li);
    }
    suggestionsList.appendChild(card);
  });
}

async function loadSuggestions() {
  const token = tokenInput.value.trim();
  const instagramText = instagramInput.value.trim();
  persistToken(token);

  refreshBtn.disabled = true;
  setStatus(
    instagramText
      ? "Analyzing Deriv markets + news + Instagram links…"
      : "Analyzing Deriv markets + news…"
  );

  const headers = { "Content-Type": "application/json" };
  const params = new URLSearchParams();
  if (token) {
    headers["X-Dashboard-Token"] = token;
    params.set("token", token);
  }

  try {
    const response = await fetch(`/api/suggestions?${params.toString()}`, {
      method: "POST",
      headers,
      body: JSON.stringify({ instagram_text: instagramText }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = payload.detail;
      throw new Error(
        typeof detail === "string" ? detail : detail ? JSON.stringify(detail) : `Request failed (${response.status})`
      );
    }
    renderReport(payload);
    setStatus(
      payload.cache_hit
        ? `Updated ${payload.generated_at} (cached)`
        : `Updated ${payload.generated_at}`
    );
  } catch (err) {
    setStatus(err.message || "Failed to load suggestions", true);
  } finally {
    refreshBtn.disabled = false;
  }
}

tokenInput.value = savedToken();
refreshBtn.addEventListener("click", loadSuggestions);

const bootParams = new URLSearchParams(window.location.search);
if (bootParams.get("token")) {
  tokenInput.value = bootParams.get("token");
  persistToken(tokenInput.value);
}
if (bootParams.get("instagram")) {
  instagramInput.value = bootParams.get("instagram");
}
