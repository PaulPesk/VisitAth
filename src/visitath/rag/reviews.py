"""Loading and cleaning of guest reviews."""
from langdetect import DetectorFactory, detect

DetectorFactory.seed = 0  # επαναλήψιμα αποτελέσματα
import re

import pandas as pd

MIN_CHARS = 30

# Automatic Airbnb messages, not real guest feedback
AUTO_PATTERNS = [
    "the host canceled this reservation",
    "the reservation was canceled",
    "this is an automated posting",
]


def strip_html(text: str) -> str:
    """Replace <br/> and other tags with spaces and normalise whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def is_automatic(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in AUTO_PATTERNS)


def clean_reviews(
    reviews: pd.DataFrame,
    listing_ids,
    max_per_listing: int = 30,
) -> pd.DataFrame:
    """Clean reviews and keep the most recent ones per listing."""
    df = reviews[reviews["listing_id"].isin(listing_ids)].copy()
    df = df.dropna(subset=["comments"])
    df["comments"] = df["comments"].astype(str).apply(strip_html)

    df = df[df["comments"].str.len() >= MIN_CHARS]
    df = df[~df["comments"].apply(is_automatic)]

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=False)
    df = df.drop_duplicates(subset="id")
    df = df.groupby("listing_id").head(max_per_listing)
    
    return df.rename(columns={"id": "review_id"})[
        ["review_id", "listing_id", "date", "comments"]
    ].reset_index(drop=True)
def detect_lang(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "unk"


def keep_english(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only reviews detected as English."""
    langs = df["comments"].apply(detect_lang)
    return df[langs == "en"].reset_index(drop=True)