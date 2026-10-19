22 September, 2026
# VisitAth

A RAG + ML assistant that recommends value-for-money Airbnb stays in Athens.
Users describe what they want in natural language (e.g. "place for 2 near the
Acropolis, under $100") and get 2-3 recommendations with explanations grounded
in real guest reviews.

> Status: work in progress. Pricing model done; RAG, LLM layer and API in development.

## How it works

1. **LLM** parses the request into filters (area, guests, budget).
2. **Filters** narrow down the listings.
3. **Pricing model** (LightGBM) estimates a fair price per listing; the
   *value score* shows how far the real price is below it.
4. **RAG** retrieves relevant guest reviews as evidence.
5. **LLM** writes the recommendation with citations.

## Data

- Source: [Inside Airbnb](https://insideairbnb.com), Athens, snapshot of **22 Sep 2026**.
- 15,134 raw listings -> 13,832 after cleaning.
- Prices are nightly prices as published in the dataset (shown with `$`).
- The raw data is not included in this repo (see the license on Inside Airbnb).
  To reproduce: download `listings.csv.gz` and `reviews.csv.gz` into `data/raw/`.

### Cleaning decisions
- Dropped listings without a price (~6%).
- Dropped the top and bottom 1% of prices (placeholder prices up to $45,000).
- Kept only "Entire home/apt" and "Private room" (hotel and shared rooms are too few and behave differently).
- Capped bathrooms at 5 (typo with 50 bathrooms).

## Pricing model

| Model | R² (log price) | MAE |
|---|---|---|
| Ridge (baseline) | 0.484 | $35.7 |
| LightGBM (test split) | 0.576 | $33.1 |
| LightGBM (5-fold out-of-fold) | 0.576 | $35.7 |

- Target: log(price). Split and CV are **grouped by host** to avoid leakage
  between listings of the same host.
- Features: size, bedrooms, bathrooms, location (neighbourhood, coordinates,
  distance to Syntagma), amenities, review scores, host info.
- Value score = (fair price - actual price) / fair price, computed from
  out-of-fold predictions.

## Limitations

- **Short-term rentals only**, not long-term rent.
- Data is a **snapshot**: prices and availability may have changed.
- The model explains about 58% of price variance. Part of the "value score"
  is model error, not a real deal. Listing quality filters (rating >= 4.5,
  >= 10 reviews, score between 0.10 and 0.50) are applied when recommending.
- Early stopping used the validation fold, so the reported metrics are
  slightly optimistic.
- Some prices may reflect specific dates or a base number of guests.

## Setup

(to be completed)

## Roadmap

- [x] Data cleaning and feature engineering
- [x] Pricing model and value score
- [ ] Refactor into `src/visitath/`
- [ ] RAG over guest reviews
- [ ] LLM layer (Ollama)
- [ ] FastAPI service
- [ ] Evaluation suite
- [ ] Docker, CI, deployment