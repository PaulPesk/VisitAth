"""Fill the 'relevant' column of listing_to_label.csv from judged labels.

Labels per listing: one 3-digit string per query (rank 1, 2, 3).
Query order: quiet, host, metro, clean, bed.
"""

import pandas as pd

from evaluation.retrieval_queries import QUERIES

LABELS = {
    6830986:             ["010", "100", "000", "000", "000"],
    1509384820447416630: ["000", "111", "100", "111", "000"],
    22218431:            ["100", "111", "000", "011", "100"],
    827443578683471376:  ["100", "111", "000", "010", "110"],
    708634568888721224:  ["000", "111", "111", "110", "000"],
    1085304507175670374: ["000", "110", "100", "110", "111"],
}

df = pd.read_csv("evaluation/listing_to_label.csv", dtype={"listing_id": "int64"})
query_index = {q: i for i, q in enumerate(QUERIES[:5])}

def label(row):
    code = LABELS[row["listing_id"]][query_index[row["query"]]]
    return int(code[row["rank"] - 1])

df["relevant"] = df.apply(label, axis=1)
df.to_csv("evaluation/listing_to_label.csv", index=False)
print(df.groupby("query")["relevant"].sum())
print("overall:", round(df["relevant"].mean(), 3))