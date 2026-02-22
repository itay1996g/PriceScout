from app.models.user import User
from app.models.subscription import Subscription
from app.models.search_usage import SearchUsage


def test_user_model_has_required_columns():
    cols = {c.name for c in User.__table__.columns}
    assert cols == {"id", "email", "password", "created_at"}


def test_subscription_model_has_required_columns():
    cols = {c.name for c in Subscription.__table__.columns}
    assert cols == {
        "id", "user_id", "stripe_id", "status", "plan", "current_period_end"
    }


def test_search_usage_model_has_required_columns():
    cols = {c.name for c in SearchUsage.__table__.columns}
    assert cols == {"id", "user_id", "session_id", "searched_at"}
