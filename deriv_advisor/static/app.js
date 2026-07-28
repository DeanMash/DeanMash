const tokenInput = document.getElementById("tokenInput");
const symbolsInput = document.getElementById("symbolsInput");
const symbolPicker = document.getElementById("symbolPicker");
const instagramInput = document.getElementById("instagramInput");
const refreshBtn = document.getElementById("refreshBtn");
const statusEl = document.getElementById("status");
const accountPanel = document.getElementById("accountPanel");
const accountLine = document.getElementById("accountLine");
const marketsPanel = document.getElementById("marketsPanel");
const marketsSummary = document.getElementById("marketsSummary");
const marketsList = document.getElementById("marketsList");
const newsPanel = document.getElementById("newsPanel");
const newsSummary = document.getElementById("newsSummary");
const newsList = document.getElementById("newsList");
const instagramPanel = document.getElementById("instagramPanel");
const instagramSummary = document.getElementById("instagramSummary");
const instagramList = document.getElementById("instagramList");
const suggestionsPanel = document.getElementById("suggestionsPanel");
const suggestionsList = document.getElementById("suggestionsList");

const TOKEN_KEY = "deriv_advisor_dashboard_token";
const SYMBOLS_KEY = "deriv_advisor_symbols";

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function savedToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

function persistToken(value) {
  if (value) localStorage.setItem(TOKEN_KEY, value);
  else localStorage.removeItem(TOKEN_KEY);
}

function savedSymbols() {
  return localStorage.getItem(SYMBOLS_KEY) || "";
}

function persistSymbols(value) {
  if (value) localStorage.setItem(SYMBOLS_KEY, value);
  else localStorage.removeItem(SYMBOLS_KEY);
}

function selectedSymbolsFromPicker() {
  return [...symbolPicker.querySelectorAll('input[type="checkbox"]:checked')].map((el) => el.value);
}

function syncSymbolsInputFromPicker() {
  const selected = selectedSymbolsFromPicker();
  if (selected.length) {
    symbolsInput.value = selected.join(", ");
  }
}

function renderIdeaCard(idea, index) {
  const card = document.createElement("article");
  card.className = "idea";
  card.style.animationDelay = `${index * 0.04}s`;
  const direction = String(idea.direction || "").toLowerCase();
  const title = idea.display_name || idea.symbol;
  card.innerHTML = `
    <div class="idea-top">
      <div>
        <div class="idea-symbol">${title}</div>
        <div class="idea-meta">${idea.symbol} · Last ${idea.last_price}</div>
      </div>
      <div>
        <span class="badge ${direction}">${idea.direction}</span>
        <div class="confidence">${Number(idea.confidence).toFixed(1)}% confidence</div>
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
  if (!idea.reasons || !idea.reasons.length) {
    const li = document.createElement("li");
    li.textContent = `RSI ${idea.rsi ?? "—"} · momentum ${(idea.momentum_pct ?? 0).toFixed?.(3) ?? idea.momentum_pct}%`;
    reasons.appendChild(li);
  }
  return card;
}

function renderReport(data) {
  accountPanel.hidden = false;
  marketsPanel.hidden = false;
  newsPanel.hidden = false;
  instagramPanel.hidden = false;
  suggestionsPanel.hidden = false;

  accountLine.textContent = `${data.account.loginid} · ${data.account.type} · ${data.account.balance.toFixed(2)} ${data.account.currency}`;

  const markets = data.markets || data.technicals || [];
  marketsSummary.textContent = `${markets.length} indices analyzed. CALL/PUT/HOLD shown for every watched market.`;
  marketsList.innerHTML = "";
  if (!markets.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No indices returned. Check DERIV_SYMBOLS or pick indices above.";
    marketsList.appendChild(empty);
  } else {
    markets.forEach((market, index) => {
      marketsList.appendChild(renderIdeaCard(market, index));
    });
  }

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
    empty.textContent = `No top ideas met the ${data.min_confidence}% confidence threshold. See All watched indices above.`;
    suggestionsList.appendChild(empty);
    return;
  }

  data.suggestions.forEach((idea, index) => {
    suggestionsList.appendChild(renderIdeaCard(idea, index));
  });
}

async function loadHealthAndPicker() {
  try {
    const response = await fetch("/api/health");
    const health = await response.json();
    const available = health.available_indices || [];
    const defaults = new Set(health.default_symbols || health.symbols || []);
    const saved = new Set(
      (savedSymbols() || "")
        .split(",")
        .map((s) => s.trim().toUpperCase())
        .filter(Boolean)
    );
    const selected = saved.size ? saved : defaults;

    symbolPicker.innerHTML = "";
    for (const item of available) {
      const id = `sym_${item.symbol}`;
      const label = document.createElement("label");
      label.className = "symbol-chip";
      label.htmlFor = id;
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.id = id;
      checkbox.value = item.symbol;
      checkbox.checked = selected.has(item.symbol);
      checkbox.addEventListener("change", syncSymbolsInputFromPicker);
      const text = document.createElement("span");
      text.textContent = item.display_name;
      label.appendChild(checkbox);
      label.appendChild(text);
      symbolPicker.appendChild(label);
    }
    syncSymbolsInputFromPicker();
  } catch (err) {
    setStatus("Could not load index list from server.", true);
  }
}

async function loadSuggestions() {
  const token = tokenInput.value.trim();
  const instagramText = instagramInput.value.trim();
  syncSymbolsInputFromPicker();
  const symbolsText = symbolsInput.value.trim();
  persistToken(token);
  persistSymbols(symbolsText);

  refreshBtn.disabled = true;
  setStatus("Analyzing your watched indices…");

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
      body: JSON.stringify({
        instagram_text: instagramText,
        symbols_text: symbolsText,
      }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = payload.detail;
      throw new Error(
        typeof detail === "string"
          ? detail
          : detail
            ? JSON.stringify(detail)
            : `Request failed (${response.status})`
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
if (savedSymbols()) symbolsInput.value = savedSymbols();
refreshBtn.addEventListener("click", loadSuggestions);

const bootParams = new URLSearchParams(window.location.search);
if (bootParams.get("token")) {
  tokenInput.value = bootParams.get("token");
  persistToken(tokenInput.value);
}
if (bootParams.get("instagram")) {
  instagramInput.value = bootParams.get("instagram");
}
if (bootParams.get("symbols")) {
  symbolsInput.value = bootParams.get("symbols");
  persistSymbols(symbolsInput.value);
}

loadHealthAndPicker();
