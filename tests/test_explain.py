import json

from visitath.llm import explain as ex


def test_explain_attaches_the_source_review(monkeypatch):
    hits = [{"review_id": "111", "text": "The flat is very quiet at night.", "distance": 0.3}]
    fake = json.dumps({"claims": [{"review": 1, "quote": "very quiet", "stance": "positive"}]})
    monkeypatch.setattr(ex, "ask", lambda *args, **kwargs: fake)

    out = ex.explain({"price": 80, "fair_price": 100}, hits, "quiet", topic="quiet")

    assert out["claims"][0]["review_id"] == "111"
    assert out["claims"][0]["review_text"] == hits[0]["text"]


def test_explain_drops_quotes_not_in_the_review(monkeypatch):
    hits = [{"review_id": "111", "text": "Nice place near the metro.", "distance": 0.3}]
    fake = json.dumps({"claims": [{"review": 1, "quote": "very quiet", "stance": "positive"}]})
    monkeypatch.setattr(ex, "ask", lambda *args, **kwargs: fake)

    out = ex.explain({"price": 80, "fair_price": 100}, hits, "quiet", topic="quiet")

    assert out["claims"] == []