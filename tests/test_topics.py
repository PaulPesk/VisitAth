import pytest

from visitath.llm.topics import resolve_topic


@pytest.mark.parametrize(
    "text, expected",
    [
        ("κάτι ήσυχο στο Θησείο", "quiet"),
        ("close to the metro, 3 people", "metro"),
        ("2 bedroom apartment in Plaka", None),
        ("σπίτι για 2 κοντά στην Ακρόπολη", None),
        ("flat with fast wifi", "wifi"),
        ("clean and quiet place", "clean"),
    ],
)
def test_resolve_topic(text, expected):
    assert resolve_topic(text) == expected