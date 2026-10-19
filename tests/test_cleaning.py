import pandas as pd

from visitath.data.cleaning import clean_listings, parse_price


def test_parse_price_handles_dollar_and_commas():
    s = pd.Series(["$85.00", "$1,250.50"])
    assert parse_price(s).tolist() == [85.0, 1250.5]


def test_clean_listings_drops_missing_price_and_other_room_types():
    raw = pd.DataFrame(
        {
            "price": ["$50.00", None, "$60.00", "$70.00"] + ["$80.00"] * 96,
            "room_type": ["Entire home/apt", "Entire home/apt", "Hotel room", "Private room"]
            + ["Entire home/apt"] * 96,
        }
    )
    out = clean_listings(raw)
    assert out["price_num"].notna().all()
    assert set(out["room_type"]) <= {"Entire home/apt", "Private room"}