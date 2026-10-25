# VisitAth

A RAG + ML assistant that recommends value-for-money Airbnb stays in Athens.
Users describe what they want in plain English or Greek (for example
*"quiet apartment for 2 in Koukaki under 120"*) and get up to three
recommendations, each with a price verdict computed in code and guest-review
quotes that are verified against the source text.

![CI](https://github.com/PaulPesk/VisitAth/actions/workflows/ci.yml/badge.svg)
## How it works

```
request -> parser (LLM) -> filters -> rank by value score -> RAG over reviews
        -> verified quotes + price verdict -> JSON
```

1. **Parser (LLM, Ollama).** Turns the request into structured filters:
   guests, neighbourhood, max price per night and an optional topic
   (quiet, bed, clean, metro, wifi, ...). Output is validated with Pydantic.
   Neighbourhoods must come from the real list in the data, and a small alias
   table in code maps common names (for example "Plaka") to official ones.
2. **Filtering and ranking.** Listings are filtered by the user's constraints
   and a quality band (rating >= 4.5, >= 10 reviews, value score between 0.10
   and 0.50), then ranked by value score.
3. **Pricing model (LightGBM).** Predicts a "fair" nightly price from listing
   features. The *value score* is `(fair price - actual price) / fair price`.
4. **RAG over guest reviews.** English reviews are embedded with
   `all-MiniLM-L6-v2` and stored in ChromaDB. For each recommended listing, the
   most relevant reviews for the requested topic are retrieved.
5. **Verified explanation.** The LLM proposes quotes with review numbers.
   Code then checks that each quote appears verbatim in the cited review and
   that it contains a keyword for the requested topic. Anything that fails is
   dropped. The price verdict is computed in code, never by the LLM.

### Why quotes are verified in code
An early version let the LLM write free text. It produced a confident summary
that misread a sentence ("very quiet *despite* being in the middle of it all")
and described the price relation vaguely. The current design restricts the LLM
to proposing quotes and lets code validate them.

## Data

- Source: [Inside Airbnb](https://insideairbnb.com), Athens,
  snapshot of **22 September 2026**.
- Listings: 15,134 raw -> **13,832** after cleaning.
- Reviews: 986,851 raw -> 236,621 after cleaning (most recent 30 per listing)
  -> **146,722 English reviews** covering 11,486 listings.
- Prices are nightly prices as published in the dataset (shown with `$`).
- The raw data is **not** included in this repository. Check the Inside Airbnb
  license before redistributing anything derived from it.

### Cleaning decisions
- Dropped listings without a price (~6%).
- Dropped the top and bottom 1% of prices (placeholder prices up to $45,000).
- Kept only "Entire home/apt" and "Private room" (hotel and shared rooms are
  too few and behave differently).
- Capped bathrooms at 5 (one listing had 50).
- Reviews: removed HTML, very short texts (< 30 characters), automatic Airbnb
  messages and duplicate review ids; kept English only (language detection with
  `langdetect`).

## Results

All numbers below were measured on this dataset. Several test sets are small
and some labels were produced by an LLM, so treat them as indicative.

| Component | Result | Caveat |
|---|---|---|
| Pricing model (LightGBM, 5-fold CV grouped by host) | R² 0.576 (log price), MAE $35.7 | Ridge baseline: R² 0.484, MAE $35.7 on a single split. Early stopping used the validation fold, so slightly optimistic |
| Retrieval over the whole review base | precision@5 ~ 1.0 (10 questions) | Easy test: thousands of near-identical reviews exist. Relevance judged by an LLM |
| Retrieval inside a single listing | precision@3 = 0.43 (6 listings x 5 topics, 90 judgements) | LLM-labelled, small sample. Low because top-3 is always returned, even when a listing has nothing relevant |
| Filter parser | 16/18 before a prompt fix, 18/18 after | The second number is optimistic: the fix targeted those exact cases |
| Topic parser | 9/10 on two sets before a rule-based fallback; 10/10 and 10/10 after it (optimistic: the fallback was written after seeing those failures); 7/8 on a third set written afterwards | Greek requests were the weak spot. Mixed requests such as "close to the metro and quiet" return one topic only |
| Verified explanation | Claims found in 20/20 cases where a relevant review existed in the top 3 | 30 cases, 6 listings. 4 extra claims appeared where labels said "none"; I checked them by hand and all four were correct (the relevant review was ranked 4th or 5th). LLM output is not fully deterministic |

## Limitations

- **Short-term rentals only.** This is not a long-term rent finder.
- **Snapshot data.** Prices and availability may have changed since 22 Sep 2026,
  and some prices may refer to specific dates or a base number of guests.
- **The value score includes model error.** The model explains about 58% of
  price variance, so part of the score is noise rather than a real deal.
- **Value-score band is a choice.** Top recommendations cluster right at the
  0.50 upper bound ("50% below fair price"), so I cannot tell whether they are
  all genuine deals or whether the listed price is unrepresentative.
- **Review-aware ranking is shallow.** When a topic is requested, the top 10
  candidates are re-ordered: listings with a positive quote first, then silent
  ones, then those with only negative quotes. The stance label comes from the
  LLM and is not verified. Checked on a single request. Response time grows
  because up to 10 listings are explained per request.
- **One topic per request**, English reviews only, and a keyword-based topic
  filter (for example "sleep" or "hot" can match loosely).
- Listing names can be in any script (some are Chinese).
- Retrieval quality for very short topic queries was checked on a single request.

## Project structure

```
src/visitath/
  data/       cleaning.py, features.py
  pricing/    model.py (LightGBM, out-of-fold value scores), build.py
  rag/        reviews.py, build_reviews.py, index.py, retrieve.py
  llm/        client.py, parse.py, aliases.py, topics.py, explain.py
  recommend.py
  api/        main.py (FastAPI)
evaluation/   retrieval, parser, topic and explain evaluation scripts
notebooks/    data exploration and pricing experiments
tests/        pytest suite
```

## Setup

Requirements: Python 3.10+, [Ollama](https://ollama.com). Developed on
Python 3.14, Windows, with an NVIDIA GPU (the 8B model fits in GPU memory,
but it also runs on CPU, only slower).

```bash
git clone https://github.com/PaulPesk/VisitAth.git
cd VisitAth
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .

ollama pull llama3.1:8b
```

Download `listings.csv.gz` and `reviews.csv.gz` for Athens from Inside Airbnb
into `data/raw/`, then build everything from the project root:

```bash
python -m visitath.pricing.build          # cleaning, features, value scores
python -m visitath.rag.build_reviews      # review cleaning + English filter (10-20 min)
python -m visitath.rag.index              # embeddings + ChromaDB (~30 min on CPU)
```

## Run

```bash
python -m uvicorn visitath.api.main:app --reload
```

- `GET /health` returns `{"status": "ok"}`
- `POST /recommend` with `{"text": "quiet apartment for 2 in Koukaki under 120"}`
- Interactive docs: http://127.0.0.1:8000/docs

Listing ids are returned as strings because they exceed the safe integer range
of JavaScript.

Example response (shortened):

```json
{
  "id": "44449129",
  "name": "Acropolis museum-for4-studioA@ 50m Acropolis metro",
  "neighbourhood": "ΚΟΥΚΑΚΙ-ΜΑΚΡΥΓΙΑΝΝΗ",
  "price_per_night": 50.21,
  "price_verdict": "50% below the estimated fair price ($100)",
  "claims": [
    {"review": 1, "quote": "you can feel the noise very loudly inside the building and outside", "stance": "negative"}
  ],
  "note": null
}
```
## Docker

The image contains only the code and API dependencies. Data, the Chroma index
and the LLM stay outside, because the data has its own license and the index
and model are large.

```bash
docker build -t visitath .

# Ollama must listen on all interfaces so the container can reach it
# (PowerShell): $env:OLLAMA_HOST="0.0.0.0:11434"; ollama serve

docker run --rm -p 8000:8000 \
  -v "$PWD/data:/app/data" \
  -v "$PWD/chroma_db:/app/chroma_db" \
  visitath
```

The container reaches Ollama through `OLLAMA_HOST`
(default `http://host.docker.internal:11434`). You still need the processed
data, the Chroma index and a running Ollama; the image is not self-contained.
## Tests

```bash
python -m pytest -v
```

16 tests cover cleaning, feature parsing, the model feature matrix, review
cleaning and API input validation. Evaluation scripts live in `evaluation/`
(for example `python -m evaluation.parse_eval`) and need Ollama running.

## Roadmap

- [x] Data cleaning and feature engineering
- [x] Pricing model with out-of-fold value scores
- [x] RAG index over English reviews
- [x] LLM request parser with validation
- [x] Verified, review-grounded explanations
- [x] FastAPI service with tests
- [x] Re-rank by review sentiment for the requested topic
- [x] Better retrieval (sentence-level chunks, hybrid BM25 + vectors)
- [ ] Fix topic parser misses and add unseen test cases
- [x] Docker, CI (GitHub Actions), deployment, request logging and rate limiting
- [ ] Multilingual reviews

## License

MIT for the code. Data from Inside Airbnb is subject to its own license.