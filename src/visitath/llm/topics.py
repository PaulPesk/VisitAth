"""Topic keywords: decide whether a quote is really about what the guest asked."""

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
    q = quote.lower() + " "
    return any(k in q for k in TOPICS.get(topic, []))