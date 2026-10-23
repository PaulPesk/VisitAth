"""End-to-end recommendation: parse -> filter -> rank -> explain."""

from pathlib import Path

import pandas as pd

from visitath.llm.explain import explain
from visitath.llm.parse import parse_request
from visitath.rag.retrieve import search_reviews

LISTINGS = Path("data/processed/listings_scored.csv")

MIN_RATING = 4.5
MIN_REVIEWS = 10
MIN_VALUE, MAX_VALUE = 0.10, 0.50  # same quality band used in the notebook

TOPIC_LABELS = {
    "quiet": "quiet",
    "bed": "the bed",
    "clean": "cleanliness",
    "metro": "the metro",
    "wifi": "wifi",
    "ac": "air conditioning",
    "checkin": "check-in",
    "host": "the host",
    "view": "the view",
    "safety": "safety",
}


def load_listings() -> pd.DataFrame:
    return pd.read_csv(LISTINGS, dtype={"id": "int64"})


def filter_and_rank(df: pd.DataFrame, filters, top_n: int = 3) -> pd.DataFrame:
    """Apply the user's filters and the quality band, rank by value score."""
    out = df
    if filters.guests is not None:
        out = out[out["accommodates"] >= filters.guests]
    if filters.neighbourhood is not None:
        out = out[out["neighbourhood_cleansed"] == filters.neighbourhood]
    if filters.max_price is not None:
        out = out[out["price_num"] <= filters.max_price]

    out = out[
        (out["review_scores_rating"] >= MIN_RATING)
        & (out["number_of_reviews"] >= MIN_REVIEWS)
        & (out["value_score"] >= MIN_VALUE)
        & (out["value_score"] <= MAX_VALUE)
    ]
    return out.sort_values("value_score", ascending=False).head(top_n)


def recommend(text: str, top_n: int = 3) -> list[dict]:
    df = load_listings()
    hoods = sorted(df["neighbourhood_cleansed"].unique())
    filters = parse_request(text, hoods)
    if filters is None:
        return []

    label = TOPIC_LABELS.get(filters.topic)
    results = []
    for _, r in filter_and_rank(df, filters, top_n).iterrows():
        listing = {"price": r["price_num"], "fair_price": r["fair_price"]}
        if filters.topic is None:
            # nothing specific to verify in the reviews
            out = explain(listing, [], "", topic=None)
            out["note"] = None
        else:
            hits = search_reviews(label, listing_id=int(r["id"]), k=5)
            out = explain(listing, hits, label, topic=filters.topic)

        results.append(
            {
                "id": str(int(r["id"])),
                "name": r["name"],
                "neighbourhood": r["neighbourhood_cleansed"],
                "price_per_night": float(r["price_num"]),
                "price_verdict": out["price"],
                "claims": out["claims"],
                "note": out["note"],
            }
        )
    return results