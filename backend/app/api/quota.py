from sqlalchemy.orm import Session

from app.config import settings
from app.models.search_usage import SearchUsage
from app.models.subscription import Subscription


def check_search_quota(
    db: Session, user_id: str | None, session_id: str
) -> tuple[bool, int]:
    """Returns (allowed, remaining). remaining=-1 means unlimited."""
    if user_id:
        subscription = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == user_id, Subscription.status == "active"
            )
            .first()
        )
        if subscription:
            return True, -1

        count = (
            db.query(SearchUsage).filter(SearchUsage.user_id == user_id).count()
        )
    else:
        count = (
            db.query(SearchUsage)
            .filter(SearchUsage.session_id == session_id)
            .count()
        )

    remaining = max(0, settings.free_search_limit - count)
    return remaining > 0, remaining
