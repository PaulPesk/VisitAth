"""Build the cleaned English reviews file used by the RAG.

Run from the project root:  python -m visitath.rag.build_reviews
"""

from pathlib import Path

import pandas as pd

from visitath.rag.reviews import clean_reviews, keep_english

RAW = Path("data/raw/reviews.csv.gz")
LISTINGS = Path("data/processed/listings_scored.csv")
OUT = Path("data/processed/reviews_clean.csv")


def main() -> None:
    listings = pd.read_csv(LISTINGS, dtype={"id": "int64"})
    reviews = pd.read_csv(RAW)
    clean = clean_reviews(reviews, listings["id"])
    print(f"After cleaning: {len(clean)} reviews")
    english = keep_english(clean)
    print(f"English only: {len(english)} reviews for {english['listing_id'].nunique()} listings")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    english.to_csv(OUT, index=False)
    print(f"Saved to {OUT}")


if __name__ == "__main__":
    main()