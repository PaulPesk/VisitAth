"""Measure explain(): finds claims when relevant reviews exist, stays silent when not."""

import pandas as pd

from evaluation.retrieval_queries import QUERIES
from visitath.llm.explain import explain
from visitath.rag.retrieve import search_reviews

TOPICS = ["quiet", "host", "metro", "clean", "bed"]
TOPIC_BY_QUERY = dict(zip(QUERIES[:5], TOPICS))

labels = pd.read_csv("evaluation/listing_labels.csv", dtype={"listing_id": "int64"})
listings = pd.read_csv("data/processed/listings_scored.csv", dtype={"id": "int64"})

rows = []
for (lid, query), g in labels.groupby(["listing_id", "query"]):
    topic = TOPIC_BY_QUERY[query]
    r = listings[listings["id"] == lid].iloc[0]
    hits = search_reviews(query, listing_id=int(lid), k=5)
    out = explain(
        {"price": r["price_num"], "fair_price": r["fair_price"]},
        hits, query, topic=topic,
    )
    has_relevant = bool(g["relevant"].max())
    got_claims = len(out["claims"]) > 0
    rows.append((lid, topic, has_relevant, got_claims))
    print(lid, topic, "relevant_exists=", has_relevant, "claims=", len(out["claims"]))

df = pd.DataFrame(rows, columns=["listing", "topic", "has_relevant", "got_claims"])
print("\nRelevant existed and claims found:", int((df.has_relevant & df.got_claims).sum()), "/", int(df.has_relevant.sum()))
print("None relevant and silent:", int((~df.has_relevant & ~df.got_claims).sum()), "/", int((~df.has_relevant).sum()))