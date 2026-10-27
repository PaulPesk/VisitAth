const form = document.getElementById("form");
const input = document.getElementById("q");
const button = document.getElementById("go");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

// Clickable examples under the search box (one is in Greek on purpose)
const EXAMPLES = [
  "Quiet apartment for 2 in Koukaki under 120",
  "Clean studio in Exarchia up to 80",
  "σπίτι για 3 άτομα στο Κολονάκι, μέχρι 150",
];

// Always textContent: names and quotes come from third parties, never HTML.
function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

// Price line plus a bar: filled up to the listed price, with a tick at the fair price
function priceBlock(r) {
  const wrap = el("div", undefined, "price");
  const line = el("div", undefined, "price-line");
  line.appendChild(el("strong", "$" + r.price_per_night.toFixed(0) + " per night"));
  line.appendChild(el("span", r.price_verdict));
  wrap.appendChild(line);

  if (typeof r.fair_price === "number") {
    const max = Math.max(r.price_per_night, r.fair_price) * 1.12;
    const track = el("div", undefined, "track");
    const fill = el("div", undefined, "fill");
    const tick = el("div", undefined, "tick");
    tick.style.left = (r.fair_price / max * 100) + "%";
    tick.title = "Estimated fair price";
    track.append(fill, tick);
    wrap.appendChild(track);

    const scale = el("div", undefined, "scale");
    scale.appendChild(el("span", "Listed price"));
    scale.appendChild(el("span", "Fair price $" + r.fair_price.toFixed(0)));
    wrap.appendChild(scale);

    // Wait two frames so the browser first paints width 0; otherwise the bar jumps
    // to its final size instead of growing
    requestAnimationFrame(() => requestAnimationFrame(() => {
      fill.style.width = (r.price_per_night / max * 100) + "%";
    }));
  }
  return wrap;
}

// Collapsible full review with the quote highlighted, so the reader can check it
function sourceReview(c) {
  const details = el("details");
  details.appendChild(el("summary", "Show the full review"));
  const box = el("p", undefined, "source");
  const text = c.review_text;
  // Find the quote inside the review (ignoring case) so we can highlight it
  const i = text.toLowerCase().indexOf(c.quote.toLowerCase());
  if (i >= 0) {
    box.appendChild(document.createTextNode(text.slice(0, i)));
    box.appendChild(el("mark", text.slice(i, i + c.quote.length)));
    box.appendChild(document.createTextNode(text.slice(i + c.quote.length)));
  } else {
    box.textContent = text;
  }
  details.appendChild(box);
  return details;
}

// One result card. The colour follows the same 10% rule as the server's price verdict
function renderCard(r) {
  const diff = typeof r.fair_price === "number"
    ? (r.price_per_night - r.fair_price) / r.fair_price : 0;
  const tone = diff <= -0.1 ? "below" : diff >= 0.1 ? "above" : "";
  const card = el("article", undefined, "card " + tone);

  card.appendChild(el("h2", r.name));
  card.appendChild(el("div", r.neighbourhood, "meta"));
  card.appendChild(priceBlock(r));

  if (r.claims.length) {
    const list = el("ul", undefined, "claims");
    r.claims.forEach(c => {
      const item = el("li", undefined, c.stance || "");
      item.appendChild(el("span", "\u201C" + c.quote + "\u201D"));
      if (c.stance === "positive") item.appendChild(el("small", "Guest praise"));
      if (c.stance === "negative") item.appendChild(el("small", "Guest complaint"));
      if (c.review_text) item.appendChild(sourceReview(c));
      list.appendChild(item);
    });
    card.appendChild(list);
  }
  if (r.note) card.appendChild(el("p", r.note, "note"));
  return card;
}

// Ignore clicks while a search is running: each search makes many LLM calls
let busy = false;

async function search(text) {
  if (busy) return;
  busy = true;
  button.disabled = true;
  resultsEl.replaceChildren();
  statusEl.className = "busy";
  statusEl.textContent = "Searching listings and reading reviews. This can take 10 to 30 seconds.";

  try {
    const res = await fetch("/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    // 429 means the server is already busy with another search
    if (res.status === 429) throw new Error("another search is still running, try again in a few seconds");
    if (!res.ok) throw new Error("the server returned " + res.status);
    const data = await res.json();

    statusEl.className = "";
    if (data.results.length === 0) {
      statusEl.textContent =
        "No listings matched. Try a higher budget, fewer guests or a different neighbourhood.";
    } else {
      statusEl.textContent = data.results.length === 1
        ? "1 stay found" : data.results.length + " stays found";
      data.results.forEach(r => resultsEl.appendChild(renderCard(r)));
    }
  } catch (err) {
    statusEl.className = "";
    statusEl.textContent = "The search failed: " + err.message + ". Check that the server and Ollama are running.";
  } finally {
    busy = false;
    button.disabled = false;
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (text.length >= 3) search(text);
});

const examplesEl = document.getElementById("examples");
EXAMPLES.forEach(t => {
  const b = el("button", t);
  b.type = "button";
  b.addEventListener("click", () => { input.value = t; search(t); });
  examplesEl.appendChild(b);
});