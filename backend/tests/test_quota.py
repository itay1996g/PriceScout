from app.api.quota import check_search_quota
from app.models.search_usage import SearchUsage
from app.models.subscription import Subscription


def test_anonymous_user_within_quota(db_session):
    """Anonymous user with 0 searches should pass quota check."""
    allowed, remaining = check_search_quota(
        db=db_session, user_id=None, session_id="sess-123"
    )
    assert allowed is True
    assert remaining == 3


def test_anonymous_user_exceeds_quota(db_session):
    """Anonymous user with 3+ searches should be blocked."""
    for _ in range(3):
        db_session.add(SearchUsage(session_id="sess-123"))
    db_session.commit()

    allowed, remaining = check_search_quota(
        db=db_session, user_id=None, session_id="sess-123"
    )
    assert allowed is False
    assert remaining == 0


def test_subscribed_user_unlimited(db_session):
    from app.models.user import User

    user = User(id="user-1", email="pro@test.com", password="x")
    db_session.add(user)
    sub = Subscription(
        user_id="user-1", stripe_id="sub_123", status="active", plan="pro"
    )
    db_session.add(sub)
    db_session.commit()

    allowed, remaining = check_search_quota(
        db=db_session, user_id="user-1", session_id="sess-456"
    )
    assert allowed is True
    assert remaining == -1  # unlimited
