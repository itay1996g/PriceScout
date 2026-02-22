from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User
from app.models.search_usage import SearchUsage
from app.models.subscription import Subscription
from app.api.deps import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str


class MeResponse(BaseModel):
    id: str
    email: str
    searches_remaining: int
    is_subscribed: bool


@router.post("/register", response_model=UserResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(email=req.email, password=hash_password(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(id=user.id, email=user.email)


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return {"token": create_token(user.id)}


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    search_count = (
        db.query(SearchUsage).filter(SearchUsage.user_id == user.id).count()
    )
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id, Subscription.status == "active")
        .first()
    )
    is_subscribed = subscription is not None
    remaining = max(0, settings.free_search_limit - search_count) if not is_subscribed else -1

    return MeResponse(
        id=user.id,
        email=user.email,
        searches_remaining=remaining,
        is_subscribed=is_subscribed,
    )
