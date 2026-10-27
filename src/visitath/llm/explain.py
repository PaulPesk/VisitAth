"""Review-grounded explanation with programmatic quote verification."""

import json

from visitath.llm.client import ask
from visitath.llm.topics import quote_matches_topic

# Only drops clearly unrelated reviews. Distances change a lot with how the question
# is worded, and a tighter cutoff threw away good matches. The real check is the
# quote verification below.
MAX_DISTANCE = 0.85

SYSTEM = """You summarise guest reviews for an Athens apartment finder.
The guest cares about: {wishes}
Reply with JSON only: {{"claims": [{{"review": <number>, "quote": "<exact words copied from that review>", "stance": "positive"|"negative"}}]}}
Rules:
- Each quote must be copied EXACTLY (at most 15 words) from the numbered review you cite.
- Only include claims that are directly relevant to what the guest cares about.
- If no review is relevant, reply {{"claims": []}}. Do not guess."""


def verified_claims(reviews: list[str], wishes: str, topic: str | None = None) -> list[dict]:
    """Ask the LLM for quotes; keep only those that really appear in the
    cited review AND are about the requested topic."""
    if not reviews:
        return []
    numbered = "\n".join(f"[{i}] {r}" for i, r in enumerate(reviews, start=1))
    raw = ask(numbered, system=SYSTEM.format(wishes=wishes), json_mode=True)
    try:
        claims = json.loads(raw).get("claims", [])
    except (ValueError, AttributeError):
        return []
    # The LLM can make quotes up, so keep a claim only if the quote really appears
    # in the review it cites and is about the topic the guest asked for
    ok = []
    for c in claims:
        try:
            n, quote = int(c["review"]), str(c["quote"]).strip().lower()
        except (KeyError, ValueError, TypeError):
            continue
        if (
            1 <= n <= len(reviews)
            and quote
            and quote in reviews[n - 1].lower()
            and quote_matches_topic(quote, topic)
        ):
            ok.append({"review": n, "quote": c["quote"], "stance": c.get("stance", "")})
    return ok


def price_verdict(price: float, fair_price: float) -> str:
    """Computed in code, never by the LLM."""
    diff = (price - fair_price) / fair_price
    if diff <= -0.10:
        return f"{abs(diff):.0%} below the estimated fair price (${fair_price:.0f})"
    if diff >= 0.10:
        return f"{diff:.0%} above the estimated fair price (${fair_price:.0f})"
    return f"close to the estimated fair price (${fair_price:.0f})"


def explain(listing: dict, hits: list[dict], wishes: str, topic: str | None = None) -> dict:
    """hits: results of search_reviews (dicts with 'review_id', 'text', 'distance')."""
    close = [h for h in hits if h["distance"] <= MAX_DISTANCE]
    claims = verified_claims([h["text"] for h in close], wishes, topic)
    for c in claims:
        # `close` is the same list the LLM saw, so its review number maps straight to an index
        source = close[c["review"] - 1]
        c["review_id"] = str(source["review_id"])
        c["review_text"] = source["text"]
    return {
        "price": price_verdict(listing["price"], listing["fair_price"]),
        "claims": claims,
        "note": None if claims else f"The reviews do not mention anything about: {wishes}.",
    }