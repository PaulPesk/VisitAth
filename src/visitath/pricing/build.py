"""Build the scored listings file used by the app.

Run from the project root:  python -m visitath.pricing.build
"""

from pathlib import Path

import pandas as pd

from visitath.data.cleaning import clean_listings
from visitath.data.features import add_features
from visitath.pricing.model import add_value_scores, evaluate

RAW = Path("data/raw/listings.csv.gz")
OUT = Path("data/processed/listings_scored.csv")


def main() -> None:
    raw = pd.read_csv(RAW)
    df = add_value_scores(add_features(clean_listings(raw)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Saved {len(df)} listings to {OUT}")
    print(evaluate(df))


if __name__ == "__main__":
    main()