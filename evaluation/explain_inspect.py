import pandas as pd

from visitath.llm.explain import explain
from visitath.rag.retrieve import search_reviews

listings = pd.read_csv("data/processed/listings_scored.csv", dtype={"id": "int64"})
CASES = [
    (6830986, "is the apartment clean?", "clean"),
    (708634568888721224, "is the apartment quiet at night?", "quiet"),
    (708634568888721224, "is the bed comfortable?", "bed"),
    (1509384820447416630, "is the apartment quiet at night?", "quiet"),
]
for lid, q, topic in CASES:
    r = listings[listings["id"] == lid].iloc[0]
    hits = search_reviews(q, listing_id=lid, k=5)
    out = explain({"price": r["price_num"], "fair_price": r["fair_price"]}, hits, q, topic=topic)
    print("\n###", lid, topic)
    for c in out["claims"]:
        print("  ->", c["quote"])