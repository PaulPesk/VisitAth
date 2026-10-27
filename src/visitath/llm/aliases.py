"""Common names -> official neighbourhood names in the dataset."""

import unicodedata

# Written by hand on purpose: a small table in code is predictable and easy to test.
# Add more names as you meet them.
ALIASES = {
    "plaka": "ΕΜΠΟΡΙΚΟ ΤΡΙΓΩΝΟ-ΠΛΑΚΑ",
    "πλακα": "ΕΜΠΟΡΙΚΟ ΤΡΙΓΩΝΟ-ΠΛΑΚΑ",
    "monastiraki": "ΕΜΠΟΡΙΚΟ ΤΡΙΓΩΝΟ-ΠΛΑΚΑ",
    "koukaki": "ΚΟΥΚΑΚΙ-ΜΑΚΡΥΓΙΑΝΝΗ",
    "κουκακι": "ΚΟΥΚΑΚΙ-ΜΑΚΡΥΓΙΑΝΝΗ",
    "exarchia": "ΜΟΥΣΕΙΟ-ΕΞΑΡΧΕΙΑ-ΝΕΑΠΟΛΗ",
    "εξαρχεια": "ΜΟΥΣΕΙΟ-ΕΞΑΡΧΕΙΑ-ΝΕΑΠΟΛΗ",
}


def normalize(text: str) -> str:
    """Lowercase and strip accents, so 'Πλάκα' and 'πλακα' match."""
    t = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def resolve_alias(text: str) -> str | None:
    """Return the official neighbourhood if the request mentions a known alias."""
    n = normalize(text)
    # Plain substring match, so keep the aliases specific
    for alias, official in ALIASES.items():
        if alias in n:
            return official
    return None