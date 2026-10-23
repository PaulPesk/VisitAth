"""HTTP API: /health and /recommend."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from visitath.recommend import recommend

app = FastAPI(title="VisitAth", version="0.1.0")


class RecommendRequest(BaseModel):
    text: str = Field(min_length=3, max_length=300)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/recommend")
def recommend_endpoint(req: RecommendRequest) -> dict:
    return {"query": req.text, "results": recommend(req.text)}