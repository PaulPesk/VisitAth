"""Turn a free-text request into structured search filters."""

import json

from pydantic import BaseModel, Field, ValidationError

from visitath.llm.client import ask


class Filters(BaseModel):
    guests: int | None = Field(default=None, ge=1, le=16)
    neighbourhood: str | None = None
    max_price: float | None = Field(default=None, gt=0)


SYSTEM = """You extract search filters for an Athens apartment finder.
Reply with JSON only, with exactly these keys:
- "guests": integer number of people, or null
- "neighbourhood": one value copied EXACTLY from the allowed list, or null
- "max_price": maximum price PER NIGHT as a number, or null
Rules:
- The user may write in Greek or English.
- Only use values the user explicitly stated. Never guess or infer a value.
  Words like "cheap" or "luxurious" do NOT give a price or a neighbourhood: use null.
- If the price is for the whole stay or several nights, or is not clearly per night, use null for max_price.
- "Athens" alone is not a neighbourhood: use null.
- Never invent a neighbourhood that is not in the list.
Allowed neighbourhoods: {hoods}"""


def parse_request(text: str, neighbourhoods: list[str]) -> Filters | None:
    system = SYSTEM.format(hoods=", ".join(neighbourhoods))
    raw = ask(text, system=system, json_mode=True)
    try:
        filters = Filters(**json.loads(raw))
    except (ValueError, ValidationError):
        return None
    if filters.neighbourhood not in (None, *neighbourhoods):
        filters.neighbourhood = None
    return filters