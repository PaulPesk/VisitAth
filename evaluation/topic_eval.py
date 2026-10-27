import pandas as pd

from evaluation.topic_cases import TOPIC_CASES
from evaluation.topic_cases_unseen import UNSEEN_CASES
from evaluation.topic_cases_unseen1 import FRESH_CASES
from visitath.llm.parse import parse_request

hoods = sorted(pd.read_csv("data/processed/listings_scored.csv")["neighbourhood_cleansed"].unique())


def run(name, cases):
    ok = 0
    for text, expected in cases:
        f = parse_request(text, hoods)
        got = f.topic if f else None
        ok += got == expected
        print(("OK  " if got == expected else "DIFF"), text, "->", got, "(expected", expected, ")")
    print(f"{name}: {ok}/{len(cases)}\n")


run("seen", TOPIC_CASES)
run("unseen", UNSEEN_CASES)
run("fresh", FRESH_CASES)