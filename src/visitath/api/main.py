"""HTTP API: /health, /recommend and a minimal web page at /."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from visitath.recommend import recommend

STATIC = Path(__file__).parent / "static"

app = FastAPI(title="VisitAth", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class RecommendRequest(BaseModel):
    text: str = Field(min_length=3, max_length=300)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/recommend")
def recommend_endpoint(req: RecommendRequest) -> dict:
    return {"query": req.text, "results": recommend(req.text)}