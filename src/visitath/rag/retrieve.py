"""Retrieve guest reviews relevant to a question."""

import chromadb
from sentence_transformers import SentenceTransformer

from visitath.rag.index import COLLECTION, DB_PATH, MODEL_NAME

_model = None
_collection = None


def _load():
    global _model, _collection
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
        _collection = chromadb.PersistentClient(path=DB_PATH).get_collection(COLLECTION)
    return _model, _collection


def search_reviews(query: str, listing_id: int | None = None, k: int = 5) -> list[dict]:
    """Top-k reviews for the query, optionally restricted to one listing."""
    model, col = _load()
    emb = model.encode([query], normalize_embeddings=True)
    res = col.query(
        query_embeddings=emb.tolist(),
        n_results=k,
        where={"listing_id": listing_id} if listing_id is not None else None,
    )
    return [
        {"review_id": rid, "listing_id": meta["listing_id"], "text": doc, "distance": dist}
        for rid, meta, doc, dist in zip(
            res["ids"][0], res["metadatas"][0], res["documents"][0], res["distances"][0]
        )
    ]