"""Score the labelled listing_to_label.csv and export a copy without review text.

listing_labels.csv holds only ids and 0/1 labels, so it is safe to commit.
"""

import pandas as pd

df = pd.read_csv("evaluation/listing_to_label.csv")
print(df.groupby("query")["relevant"].mean().round(2))
print("overall:", round(df["relevant"].mean(), 3))
df[["query", "listing_id", "review_id", "relevant"]].to_csv(
    "evaluation/listing_labels.csv", index=False
)