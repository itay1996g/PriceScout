import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

from app.agent.runner import run_search_agent
from app.api.quota import check_search_quota
from app.db import get_db
from app.models.search_usage import SearchUsage
from app.models.user import User

router = APIRouter(prefix="/api", tags=["search"])


class SearchRequest(BaseModel):
    query: str


def _get_session_id(request: Request) -> str:
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


def _get_optional_user(request: Request, db: Session) -> User | None:
    """Try to get the current user from JWT, return None if not authenticated."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    try:
        import jwt as pyjwt

        from app.config import settings

        token = auth_header.split(" ")[1]
        payload = pyjwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        return db.query(User).filter(User.id == user_id).first()
    except Exception:
        return None


@router.post("/search")
async def search(req: SearchRequest, request: Request, db: Session = Depends(get_db)):
    session_id = _get_session_id(request)
    user = _get_optional_user(request, db)
    user_id = user.id if user else None

    allowed, remaining = check_search_quota(db, user_id, session_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Search quota exceeded. Please subscribe for unlimited searches.",
        )

    # Record the search
    usage = SearchUsage(user_id=user_id, session_id=session_id)
    db.add(usage)
    db.commit()

    async def event_generator():
        async for event in run_search_agent(req.query):
            yield {"data": json.dumps(event)}

    response = EventSourceResponse(event_generator())
    if not request.cookies.get("session_id"):
        response.set_cookie("session_id", session_id, max_age=60 * 60 * 24 * 365)
    return response
