"""Topic keywords: decide whether a quote is really about what the guest asked."""
import re

from visitath.llm.aliases import normalize

# Keywords used to check that a quote is really about the topic the guest asked for.
# They are loose on purpose: "hot" also matches "hot water", "sleep" matches "slept great".
TOPICS = {
    "quiet": ["quiet", "noise", "noisy", "peaceful", "loud", "silent", "sleep"],
    "bed": ["bed", "mattress", "pillow", "sheets", "sofa bed", "couch"],
    "clean": ["clean", "spotless", "tidy", "dirty", "dust", "smell", "bugs", "ants"],
    "metro": ["metro", "subway", "station", "tram", "bus", "transport"],
    "wifi": ["wifi", "wi-fi", "internet"],
    "ac": ["air conditioning", "air-conditioning", "aircon", "a/c", "ac ", "heating", "hot", "cold"],
    "checkin": ["check in", "check-in", "checkin", "check out", "check-out", "key", "self check", "arrival"],
    "host": ["host", "responsive", "communicat", "helpful", "owner"],
    "view": ["view", "acropolis", "balcony", "terrace"],
    "safety": ["safe", "safety", "unsafe", "rough", "dangerous"],
}


def quote_matches_topic(quote: str, topic: str | None) -> bool:
    """True if the quote contains a keyword of the topic. No topic = no filtering."""
    if topic is None:
        return True
    # Pad with a space so entries like "ac " also match when "ac" is the last word
    q = quote.lower() + " "
    return any(k in q for k in TOPICS.get(topic, []))
# Patterns for spotting the topic in the guest's request. They run on normalised text
# (lowercase, no accents), so "ήσυχο" becomes "ησυχο". The \b markers stop "bed"
# from matching inside "bedroom".
TOPIC_PATTERNS = {
    "quiet": [r"\bquiet", r"\bnois", r"\bpeaceful", r"ησυχ", r"θορυβ"],
    "bed": [r"\bbeds?\b", r"mattress", r"κρεβατ", r"στρωμα"],
    "clean": [r"\bclean", r"\bspotless", r"καθαρ"],
    "metro": [r"\bmetro\b", r"\bsubway\b", r"\bμετρο\b"],
    "wifi": [r"wi-?fi", r"\binternet\b"],
    "ac": [r"air.?condition", r"\ba/?c\b", r"aircon", r"κλιματισμ"],
    "checkin": [r"check.?in", r"check.?out"],
    "host": [r"\bhost\b", r"\bresponsive\b"],
    "view": [r"\bviews?\b", r"\bθεα(ς)?\b"],
    "safety": [r"\bsafe", r"\bunsafe", r"ασφαλ"],
}


def resolve_topic(text: str) -> str | None:
    """Topic named in the request, or None. If several, the first mentioned wins."""
    n = normalize(text)
    best = None
    for topic, patterns in TOPIC_PATTERNS.items():
        for p in patterns:
            m = re.search(p, n)
            if m and (best is None or m.start() < best[0]):
                best = (m.start(), topic)
    return best[1] if best else None