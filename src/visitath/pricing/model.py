"""Fair-price model (LightGBM) and value score."""

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold

NUMERIC_FEATURES = [
    "accommodates", "bedrooms", "beds", "baths", "shared_bath",
    "latitude", "longitude", "dist_center_km",
    "review_scores_rating", "review_scores_location", "number_of_reviews",
    "has_reviews", "minimum_nights", "availability_365", "is_superhost",
    "n_amenities", "has_wifi", "has_ac", "has_kitchen", "has_balcony",
    "has_elevator", "has_parking",
]
CATEGORICAL_FEATURES = ["room_type", "neighbourhood_cleansed"]

LGB_PARAMS = {
    "n_estimators": 2000,
    "learning_rate": 0.03,
    "num_leaves": 31,
    "min_child_samples": 20,
    "subsample": 0.8,
    "subsample_freq": 1,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "verbose": -1,
}


def build_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Select model features and set categorical dtypes."""
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    for c in CATEGORICAL_FEATURES:
        X[c] = X[c].astype("category")
    return X


def out_of_fold_fair_price(df: pd.DataFrame, n_splits: int = 5) -> np.ndarray:
    """Fair price per listing from models that never saw that listing.

    Folds are grouped by host to avoid leakage between a host's listings.
    """
    X = build_matrix(df)
    y = np.log(df["price_num"])
    oof = np.zeros(len(df))

    for tr, va in GroupKFold(n_splits=n_splits).split(X, y, df["host_id"]):
        model = lgb.LGBMRegressor(**LGB_PARAMS)
        model.fit(
            X.iloc[tr], y.iloc[tr],
            eval_set=[(X.iloc[va], y.iloc[va])],
            callbacks=[lgb.early_stopping(100, verbose=False)],
        )
        oof[va] = model.predict(X.iloc[va])
    return np.exp(oof)


def add_value_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Add fair_price and value_score columns."""
    out = df.copy()
    out["fair_price"] = out_of_fold_fair_price(out)
    out["value_score"] = (out["fair_price"] - out["price_num"]) / out["fair_price"]
    return out


def evaluate(df: pd.DataFrame) -> dict:
    """R² (log) and MAE ($) of the fair-price predictions."""
    return {
        "r2_log": r2_score(np.log(df["price_num"]), np.log(df["fair_price"])),
        "mae": mean_absolute_error(df["price_num"], df["fair_price"]),
    }