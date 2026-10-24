from visitath.recommend import review_group


def test_review_group_orders_positive_before_silent_before_negative():
    pos = [{"stance": "positive"}, {"stance": "negative"}]
    neg = [{"stance": "negative"}]
    assert review_group(pos) == 0
    assert review_group([]) == 1
    assert review_group(neg) == 2