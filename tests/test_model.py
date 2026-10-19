import pandas as pd

from visitath.pricing.model import build_matrix, NUMERIC_FEATURES, CATEGORICAL_FEATURES


def test_build_matrix_has_expected_columns_and_categories():
    row = {c: 1 for c in NUMERIC_FEATURES}
    row.update({"room_type": "Private room", "neighbourhood_cleansed": "ΠΛΑΚΑ"})
    X = build_matrix(pd.DataFrame([row, row]))
    assert list(X.columns) == NUMERIC_FEATURES + CATEGORICAL_FEATURES
    assert str(X["room_type"].dtype) == "category"