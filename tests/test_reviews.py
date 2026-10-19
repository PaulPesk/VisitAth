from visitath.rag.reviews import is_automatic, strip_html


def test_strip_html_removes_tags_and_extra_spaces():
    assert strip_html("Nice<br/>place <br/> here") == "Nice place here"


def test_is_automatic_detects_cancellation_text():
    assert is_automatic("The host canceled this reservation 5 days before arrival.")
    assert not is_automatic("Great location and very clean.")