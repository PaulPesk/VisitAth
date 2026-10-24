"""Turn a free-text request into structured search filters."""

import json

from pydantic import BaseModel, Field, ValidationError

from visitath.llm.aliases import resolve_alias
from visitath.llm.client import ask
from visitath.llm.topics import TOPICS


class Filters(BaseModel):
    guests: int | None = Field(default=None, ge=1, le=16)
    neighbourhood: str | None = None
    max_price: float | None = Field(default=None, gt=0)
    topic: str | None = None


SYSTEM = """You extract search filters for an Athens apartment finder.
Reply with JSON only, with exactly these keys:
- "guests": integer number of people, or null
- "neighbourhood": one value copied EXACTLY from the allowed list, or null
- "max_price": maximum price PER NIGHT as a number, or null
- "topic": the ONE quality the guest explicitly asks about, copied EXACTLY from the allowed topics, or null
Rules:
- The user may write in Greek or English.
- Only use values the user explicitly stated. Never guess or infer a value.
  Words like "cheap" or "luxurious" do NOT give a price or a neighbourhood: use null.
- If the price is for the whole stay or several nights, or is not clearly per night, use null for max_price.
- "Athens" alone is not a neighbourhood: use null.
- Never invent a neighbourhood that is not in the list.
- A place name such as "near the Acropolis" is a location, not a topic. Use topic "view" only if the guest asks about the view.
- If the guest asks about several qualities, pick the first one mentioned.
Allowed neighbourhoods: {hoods}
Allowed topics: {topics}"""


def parse_request(text: str, neighbourhoods: list[str]) -> Filters | None:
    system = SYSTEM.format(hoods=", ".join(neighbourhoods), topics=", ".join(TOPICS))
    raw = ask(text, system=system, json_mode=True)
    try:
        filters = Filters(**json.loads(raw))
    except (ValueError, ValidationError):
        return None
    if filters.neighbourhood not in (None, *neighbourhoods):
        filters.neighbourhood = None
    if filters.topic not in (None, *TOPICS):
        filters.topic = None
    alias = resolve_alias(text)
    if alias in neighbourhoods:
        filters.neighbourhood = alias
    return filters