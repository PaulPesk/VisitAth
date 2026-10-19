"""Cleaning of the raw Inside Airbnb listings."""

import pandas as pd

KEPT_ROOM_TYPES = ["Entire home/apt", "Private room"]


def parse_price(series: pd.Series) -> pd.Series:
    """Convert prices like '$1,250.00' to floats."""
    return (
        series.str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )


def clean_listings(
    raw: pd.DataFrame,
    low_q: float = 0.01,
    high_q: float = 0.99,
) -> pd.DataFrame:
    """Clean raw listings.

    Steps:
      1. Convert price to a number (price_num).
      2. Drop listings without a price.
      3. Drop the top and bottom 1% of prices (placeholder/extreme prices).
      4. Keep only the room types in KEPT_ROOM_TYPES.
    """
    df = raw.copy()
    df["price_num"] = parse_price(df["price"])
    df = df.dropna(subset=["price_num"])

    low, high = df["price_num"].quantile([low_q, high_q])
    df = df[(df["price_num"] >= low) & (df["price_num"] <= high)]

    df = df[df["room_type"].isin(KEPT_ROOM_TYPES)]
    return df.reset_index(drop=True)