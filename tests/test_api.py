from fastapi.testclient import TestClient

from visitath.api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_recommend_rejects_too_short_text():
    r = client.post("/recommend", json={"text": "hi"})
    assert r.status_code == 422


def test_recommend_rejects_too_long_text():
    r = client.post("/recommend", json={"text": "x" * 301})
    assert r.status_code == 422