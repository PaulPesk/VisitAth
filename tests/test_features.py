import numpy as np
import pandas as pd

from visitath.data.features import haversine_km, parse_amenities, parse_baths


def test_parse_baths():
    assert parse_baths("1.5 baths") == 1.5
    assert parse_baths("Half-bath") == 0.5
    assert np.isnan(parse_baths(None))


def test_parse_amenities_handles_bad_input():
    assert parse_amenities('["Wifi", "Kitchen"]') == ["wifi", "kitchen"]
    assert parse_amenities("not json") == []
    assert parse_amenities(None) == []


def test_haversine_zero_distance():
    assert haversine_km(37.97, 23.73, 37.97, 23.73) == 0
    assert haversine_km(37.97, 23.73, 37.98, 23.73) > 0