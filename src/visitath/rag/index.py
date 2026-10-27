"""Embed the cleaned reviews and store them in a Chroma vector store.

Run from the project root:  python -m visitath.rag.index
"""

from pathlib import Path

import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

REVIEWS = Path("data/processed/reviews_clean.csv")
DB_PATH = "chroma_db"
COLLECTION = "reviews"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH = 256


def main(limit: int | None = None) -> None:
    df = pd.read_csv(REVIEWS, dtype={"review_id": "int64", "listing_id": "int64"})
    # Chroma rejects duplicate ids inside one batch
    df = df.drop_duplicates(subset="review_id")
    if limit:
        df = df.head(limit)

    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=DB_PATH)
    # Cosine distance (the embeddings are normalised)
    col = client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    for start in range(0, len(df), BATCH):
        chunk = df.iloc[start : start + BATCH]
        emb = model.encode(chunk["comments"].tolist(), normalize_embeddings=True)
        # upsert, so re-running after an interruption doesn't create duplicates
        col.upsert(
            ids=chunk["review_id"].astype(str).tolist(),
            embeddings=emb.tolist(),
            documents=chunk["comments"].tolist(),
            metadatas=[{"listing_id": int(i)} for i in chunk["listing_id"]],
        )
        if (start // BATCH) % 20 == 0:
            print(f"{start + len(chunk)} / {len(df)}")
    print("Done:", col.count())


if __name__ == "__main__":
    main()