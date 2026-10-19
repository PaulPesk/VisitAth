"""Dump top-5 results per query to a CSV for manual relevance labeling."""

import csv

from evaluation.retrieval_queries import QUERIES
from visitath.rag.retrieve import search_reviews

with open("evaluation/retrieval_to_label.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["query", "rank", "listing_id", "distance", "text", "relevant"])
    for q in QUERIES:
        for rank, r in enumerate(search_reviews(q, k=5), start=1):
            w.writerow([q, rank, r["listing_id"], round(r["distance"], 3), r["text"], ""])
print("Saved evaluation/retrieval_to_label.csv")