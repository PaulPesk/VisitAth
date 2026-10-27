"""Feature engineering for cleaned listings."""

import json
import re

import numpy as np
import pandas as pd

CENTER_LAT, CENTER_LON = 37.9755, 23.7348  # Syntagma Square, used as "the city centre"

# Flag name -> keyword to look for inside the amenity texts
AMENITY_FLAGS = {
    "has_wifi": "wifi",
    "has_ac": "air conditioning",
    "has_kitchen": "kitchen",
    "has_balcony": "balcony",
    "has_elevator": "elevator",
    "has_parking": "parking",
}


def parse_baths(text) -> float:
    """Extract the number of bathrooms from text like '1.5 shared baths'."""
    if pd.isna(text):
        return np.nan
    t = str(text).lower()
    m = re.search(r"(\d+(\.\d+)?)", t)
    if m:
        return float(m.group(1))
    # "Half-bath" has no digit, so it needs its own case
    return 0.5 if "half" in t else np.nan


def parse_amenities(s) -> list[str]:
    """Parse the JSON amenities string into a lowercase list."""
    try:
        return [a.lower() for a in json.loads(s)]
    except (TypeError, ValueError):
        return []


def haversine_km(lat1, lon1, lat2, lon2):
    """Distance in km between points given in degrees."""
    r = 6371
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dl = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with the engineered features added."""
    out = df.copy()

    # Cap at 5: one listing claims 50 bathrooms
    out["baths"] = out["bathrooms_text"].apply(parse_baths).clip(upper=5)
    out["shared_bath"] = (
        out["bathrooms_text"].str.contains("shared", case=False, na=False).astype(int)
    )

    # The export writes booleans as 't' / 'f'
    out["is_superhost"] = out["host_is_superhost"].map({"t": 1, "f": 0})
    out["has_reviews"] = (out["number_of_reviews"] > 0).astype(int)

    amenity_lists = out["amenities"].apply(parse_amenities)
    out["n_amenities"] = amenity_lists.apply(len)
    for col, kw in AMENITY_FLAGS.items():
        # kw=kw freezes the loop variable; without it every lambda would use the last keyword
        out[col] = amenity_lists.apply(lambda L, kw=kw: int(any(kw in a for a in L)))

    out["dist_center_km"] = haversine_km(
        out["latitude"], out["longitude"], CENTER_LAT, CENTER_LON
    )
    return out