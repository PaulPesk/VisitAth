"""Per-listing retrieval: dump top-3 for sample listings for manual labeling."""

import csv
import random

import pandas as pd

from evaluation.retrieval_queries import QUERIES
from visitath.rag.retrieve import search_reviews

reviews = pd.read_csv("data/processed/reviews_clean.csv")
counts = reviews["listing_id"].value_counts()
pool = counts[(counts >= 15) & (counts <= 60)].index.tolist()
random.seed(0)
listings = random.sample(pool, 6)

with open("evaluation/listing_to_label.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["query", "listing_id", "rank", "review_id", "distance", "text", "relevant"])
    for lid in listings:
        for q in QUERIES[:5]:
            for rank, r in enumerate(search_reviews(q, listing_id=int(lid), k=3), start=1):
                w.writerow([q, lid, rank, r["review_id"], round(r["distance"], 3), r["text"], ""])
print("Saved evaluation/listing_to_label.csv")