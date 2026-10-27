import pandas as pd

from evaluation.parse_cases import CASES
from visitath.llm.parse import parse_request

hoods = sorted(pd.read_csv("data/processed/listings_scored.csv")["neighbourhood_cleansed"].unique())
ok = {"guests": 0, "neighbourhood": 0, "max_price": 0}

for text, g, n, p in CASES:
    f = parse_request(text, hoods)
    got = (f.guests, f.neighbourhood, f.max_price) if f else (None, None, None)
    ok["guests"] += got[0] == g
    ok["neighbourhood"] += got[1] == n
    ok["max_price"] += got[2] == p
    print(("OK  " if got == (g, n, p) else "DIFF"), text, "->", got)

print({k: f"{v}/{len(CASES)}" for k, v in ok.items()})