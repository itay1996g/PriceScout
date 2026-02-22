# PriceScout Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a location-based price comparison SaaS where an AI agent finds the best deals for any product in any location from natural language input.

**Architecture:** React (Vite) frontend sends queries to a FastAPI backend. The backend invokes a Claude agent with web_search and web_fetch tools to research products. Results stream back via SSE. PostgreSQL stores users, subscriptions, and search quotas. Stripe handles billing.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, Alembic, Anthropic SDK, Stripe, PyJWT, React 18, Vite, TypeScript, TailwindCSS, shadcn/ui

**Project Root:** `~/Desktop/Work/price-compare`

---

## Phase 1: Project Scaffolding

### Task 1: Initialize Backend Project

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`

**Step 1: Create directory structure**

```bash
mkdir -p ~/Desktop/Work/price-compare/backend/app/api
mkdir -p ~/Desktop/Work/price-compare/backend/app/agent
mkdir -p ~/Desktop/Work/price-compare/backend/app/models
mkdir -p ~/Desktop/Work/price-compare/backend/tests
```

**Step 2: Create requirements.txt**

```text
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
alembic==1.14.1
psycopg2-binary==2.9.10
anthropic==0.44.0
stripe==11.4.1
pyjwt==2.10.1
bcrypt==4.2.1
sse-starlette==2.2.1
python-dotenv==1.0.1
httpx==0.28.1
pytest==8.3.4
pytest-asyncio==0.25.0
```

**Step 3: Create config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/pricescout"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    anthropic_api_key: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""
    free_search_limit: int = 3
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
```

**Step 4: Create main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(title="PriceScout API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

**Step 5: Create .env.example**

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pricescout
JWT_SECRET=change-me-in-production
ANTHROPIC_API_KEY=sk-ant-...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
FRONTEND_URL=http://localhost:5173
```

**Step 6: Create empty __init__.py files**

```bash
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/agent/__init__.py
touch backend/app/models/__init__.py
touch backend/tests/__init__.py
```

**Step 7: Verify backend starts**

```bash
cd ~/Desktop/Work/price-compare/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# Visit http://localhost:8000/api/health → {"status": "ok"}
```

**Step 8: Commit**

```bash
cd ~/Desktop/Work/price-compare
git init
git add backend/
git commit -m "feat: initialize backend project with FastAPI"
```

---

### Task 2: Initialize Frontend Project

**Files:**
- Create: `frontend/` (Vite scaffold)
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/lib/api.ts`

**Step 1: Scaffold Vite + React + TypeScript**

```bash
cd ~/Desktop/Work/price-compare
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

**Step 2: Install dependencies**

```bash
cd ~/Desktop/Work/price-compare/frontend
npm install -D tailwindcss @tailwindcss/vite
npm install react-router-dom
```

**Step 3: Configure Tailwind**

Add Tailwind to `frontend/vite.config.ts`:

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
```

Replace contents of `frontend/src/index.css`:

```css
@import "tailwindcss";
```

**Step 4: Install shadcn/ui**

```bash
cd ~/Desktop/Work/price-compare/frontend
npx shadcn@latest init
# Select: New York style, Slate base color, CSS variables: yes
```

**Step 5: Add initial shadcn components**

```bash
npx shadcn@latest add button input card badge
```

**Step 6: Create API client**

Create `frontend/src/lib/api.ts`:

```typescript
const API_BASE = "/api";

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const token = localStorage.getItem("token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...headers, ...options?.headers },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return res.json();
}
```

**Step 7: Replace App.tsx with placeholder**

```tsx
function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <h1 className="text-4xl font-bold text-slate-900">PriceScout</h1>
    </div>
  );
}

export default App;
```

**Step 8: Verify frontend starts**

```bash
cd ~/Desktop/Work/price-compare/frontend
npm run dev
# Visit http://localhost:5173 → shows "PriceScout"
```

**Step 9: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add frontend/
git commit -m "feat: initialize frontend with Vite, React, Tailwind, shadcn"
```

---

### Task 3: Docker Compose for Local Postgres

**Files:**
- Create: `docker-compose.yml`
- Create: `.gitignore`

**Step 1: Create docker-compose.yml**

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: pricescout
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

**Step 2: Create .gitignore**

```
# Python
__pycache__/
*.pyc
.env
venv/
.venv/

# Node
node_modules/
dist/

# IDE
.idea/
.vscode/

# OS
.DS_Store
```

**Step 3: Start Postgres**

```bash
cd ~/Desktop/Work/price-compare
docker compose up -d
# Verify: docker compose ps → postgres running on 5432
```

**Step 4: Commit**

```bash
git add docker-compose.yml .gitignore
git commit -m "feat: add docker-compose for local Postgres"
```

---

## Phase 2: Backend — Database & Auth

### Task 4: SQLAlchemy Models

**Files:**
- Create: `backend/app/db.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/subscription.py`
- Create: `backend/app/models/search_usage.py`

**Step 1: Write the test**

Create `backend/tests/test_models.py`:

```python
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
```

**Step 2: Run test to verify it fails**

```bash
cd ~/Desktop/Work/price-compare/backend
python -m pytest tests/test_models.py -v
# Expected: FAIL — ModuleNotFoundError
```

**Step 3: Create db.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 4: Create user model**

Create `backend/app/models/user.py`:

```python
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
```

**Step 5: Create subscription model**

Create `backend/app/models/subscription.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    stripe_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    plan: Mapped[str] = mapped_column(String(50), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
```

**Step 6: Create search_usage model**

Create `backend/app/models/search_usage.py`:

```python
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class SearchUsage(Base):
    __tablename__ = "search_usage"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True
    )
    session_id: Mapped[str] = mapped_column(String(255), nullable=False)
    searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
```

**Step 7: Run test to verify it passes**

```bash
cd ~/Desktop/Work/price-compare/backend
python -m pytest tests/test_models.py -v
# Expected: 3 passed
```

**Step 8: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add backend/
git commit -m "feat: add SQLAlchemy models for users, subscriptions, search_usage"
```

---

### Task 5: Alembic Migrations

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/` (via alembic init)

**Step 1: Initialize Alembic**

```bash
cd ~/Desktop/Work/price-compare/backend
alembic init alembic
```

**Step 2: Update alembic/env.py**

Replace the `target_metadata` line and add imports at top of `alembic/env.py`:

```python
# At the top, add:
from app.db import Base
from app.models.user import User
from app.models.subscription import Subscription
from app.models.search_usage import SearchUsage

# Replace target_metadata = None with:
target_metadata = Base.metadata
```

Also update the `run_migrations_online` function to read DATABASE_URL from environment:

```python
from app.config import settings

def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": settings.database_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    # ... rest stays the same
```

**Step 3: Generate initial migration**

```bash
cd ~/Desktop/Work/price-compare/backend
alembic revision --autogenerate -m "initial schema"
```

**Step 4: Run migration**

```bash
alembic upgrade head
# Verify: tables created in postgres
```

**Step 5: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add backend/alembic/ backend/alembic.ini
git commit -m "feat: add Alembic migrations with initial schema"
```

---

### Task 6: Auth Endpoints

**Files:**
- Create: `backend/app/api/auth.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/tests/test_auth.py`

**Step 1: Write the failing tests**

Create `backend/tests/conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

Create `backend/tests/test_auth.py`:

```python
def test_register_creates_user(client):
    res = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_email_fails(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    res = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "otherpass",
    })
    assert res.status_code == 400


def test_login_returns_token(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    res = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    assert res.status_code == 200
    assert "token" in res.json()


def test_login_wrong_password_fails(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    res = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpass",
    })
    assert res.status_code == 401


def test_me_returns_user_info(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    login_res = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    token = login_res.json()["token"]

    res = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}",
    })
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"
    assert "searches_remaining" in res.json()


def test_me_without_token_fails(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
```

**Step 2: Run tests to verify they fail**

```bash
cd ~/Desktop/Work/price-compare/backend
python -m pytest tests/test_auth.py -v
# Expected: FAIL — 404 on all routes
```

**Step 3: Create deps.py (auth dependencies)**

Create `backend/app/api/deps.py`:

```python
from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User

security = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=settings.jwt_expiration_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
```

**Step 4: Create auth.py routes**

Create `backend/app/api/auth.py`:

```python
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
```

**Step 5: Register router in main.py**

Add to `backend/app/main.py`:

```python
from app.api.auth import router as auth_router

app.include_router(auth_router)
```

**Step 6: Run tests to verify they pass**

```bash
cd ~/Desktop/Work/price-compare/backend
python -m pytest tests/test_auth.py -v
# Expected: 6 passed
```

**Step 7: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add backend/
git commit -m "feat: add auth endpoints (register, login, me) with JWT"
```

---

### Task 7: Search Quota Checking

**Files:**
- Create: `backend/app/api/quota.py`
- Create: `backend/tests/test_quota.py`

**Step 1: Write the failing test**

Create `backend/tests/test_quota.py`:

```python
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
```

**Step 2: Run test to verify it fails**

```bash
cd ~/Desktop/Work/price-compare/backend
python -m pytest tests/test_quota.py -v
# Expected: FAIL — ImportError
```

**Step 3: Implement quota check**

Create `backend/app/api/quota.py`:

```python
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
```

**Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_quota.py -v
# Expected: 3 passed
```

**Step 5: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add backend/
git commit -m "feat: add search quota checking with subscription bypass"
```

---

## Phase 3: Backend — Agent & Search

### Task 8: Claude Agent Runner

**Files:**
- Create: `backend/app/agent/prompts.py`
- Create: `backend/app/agent/runner.py`
- Create: `backend/tests/test_agent.py`

**Step 1: Create the system prompt**

Create `backend/app/agent/prompts.py`:

```python
SYSTEM_PROMPT = """You are a product research assistant for PriceScout. Your job is to find the best deals on products in specific locations.

When the user gives you a product and location, you must:
1. Search the web for that product available in or near that location
2. Fetch promising result pages to extract exact prices, seller names, and addresses
3. Return the top 3 best offers ranked primarily by price (lowest first)

IMPORTANT RULES:
- Always search for real, current listings — never make up prices or sellers
- Include the seller's physical address or city when available
- Convert all prices to USD as a secondary display (keep original currency as primary)
- Note the product condition (new, pre-owned, refurbished) when available
- If you can't find 3 results, return as many as you found (minimum 1)
- If you genuinely can't find any results, say so honestly

You MUST respond with valid JSON matching this exact schema:

{
  "product_understood": "your interpretation of what product the user wants",
  "location": "the location you searched in",
  "results": [
    {
      "rank": 1,
      "product_name": "exact product name from listing",
      "price": "$X,XXX",
      "currency": "original currency code",
      "seller_name": "store or seller name",
      "seller_address": "address or city",
      "url": "direct link to the listing",
      "condition": "New / Pre-owned / Refurbished",
      "notes": "any relevant details (warranty, shipping, etc.)"
    }
  ],
  "search_summary": "Brief summary of what you found"
}"""
```

**Step 2: Create the agent runner**

Create `backend/app/agent/runner.py`:

```python
import json
from collections.abc import AsyncGenerator

import anthropic

from app.agent.prompts import SYSTEM_PROMPT
from app.config import settings


async def run_search_agent(query: str) -> AsyncGenerator[dict, None]:
    """Run the Claude agent and yield SSE events as dicts."""
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    yield {"status": "searching", "message": f"Researching: {query}..."}

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 10,
                },
            ],
            messages=[{"role": "user", "content": query}],
        )

        yield {"status": "analyzing", "message": "Analyzing results..."}

        # Extract the text response from the message
        text_content = ""
        for block in response.content:
            if block.type == "text":
                text_content = block.text
                break

        # Parse the JSON from the response
        # The agent should return JSON, but it might be wrapped in markdown
        json_str = text_content
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]

        data = json.loads(json_str.strip())

        yield {"status": "complete", "data": data}

    except json.JSONDecodeError:
        yield {
            "status": "complete",
            "data": {
                "product_understood": query,
                "location": "Unknown",
                "results": [],
                "search_summary": "The agent returned results in an unexpected format. Please try again.",
                "raw_response": text_content,
            },
        }
    except anthropic.APIError as e:
        yield {
            "status": "error",
            "message": f"Search failed: {str(e)}",
        }
```

**Step 3: Write a basic structure test**

Create `backend/tests/test_agent.py`:

```python
from app.agent.prompts import SYSTEM_PROMPT


def test_system_prompt_includes_json_schema():
    assert "product_understood" in SYSTEM_PROMPT
    assert "results" in SYSTEM_PROMPT
    assert "seller_name" in SYSTEM_PROMPT


def test_system_prompt_instructs_top_3():
    assert "top 3" in SYSTEM_PROMPT
```

**Step 4: Run tests**

```bash
cd ~/Desktop/Work/price-compare/backend
python -m pytest tests/test_agent.py -v
# Expected: 2 passed
```

**Step 5: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add backend/
git commit -m "feat: add Claude agent runner with web search tools and SSE events"
```

---

### Task 9: Search Endpoint with SSE

**Files:**
- Create: `backend/app/api/search.py`
- Create: `backend/tests/test_search.py`

**Step 1: Write the failing test**

Create `backend/tests/test_search.py`:

```python
from unittest.mock import patch, AsyncMock


def test_search_requires_query(client):
    res = client.post("/api/search", json={})
    assert res.status_code == 422


def test_search_checks_quota(client, db_session):
    from app.models.search_usage import SearchUsage

    # Exhaust free searches
    for _ in range(3):
        db_session.add(SearchUsage(session_id="test-session"))
    db_session.commit()

    res = client.post(
        "/api/search",
        json={"query": "test product in test city"},
        cookies={"session_id": "test-session"},
    )
    assert res.status_code == 402
    assert "quota" in res.json()["detail"].lower() or "limit" in res.json()["detail"].lower()
```

**Step 2: Run tests to verify they fail**

```bash
cd ~/Desktop/Work/price-compare/backend
python -m pytest tests/test_search.py -v
# Expected: FAIL
```

**Step 3: Implement search endpoint**

Create `backend/app/api/search.py`:

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session
import json

from app.db import get_db
from app.api.deps import get_current_user
from app.api.quota import check_search_quota
from app.agent.runner import run_search_agent
from app.models.user import User
from app.models.search_usage import SearchUsage

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

    from app.api.deps import get_current_user as _get_user
    from fastapi.security import HTTPAuthorizationCredentials

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
```

**Step 4: Register router in main.py**

Add to `backend/app/main.py`:

```python
from app.api.search import router as search_router

app.include_router(search_router)
```

**Step 5: Run tests to verify they pass**

```bash
cd ~/Desktop/Work/price-compare/backend
python -m pytest tests/test_search.py -v
# Expected: 2 passed
```

**Step 6: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add backend/
git commit -m "feat: add /search endpoint with SSE streaming and quota enforcement"
```

---

### Task 10: Stripe Billing Endpoints

**Files:**
- Create: `backend/app/api/billing.py`
- Create: `backend/tests/test_billing.py`

**Step 1: Write the failing test**

Create `backend/tests/test_billing.py`:

```python
def test_create_checkout_requires_auth(client):
    res = client.post("/api/billing/create-checkout")
    assert res.status_code in (401, 403)


def test_create_checkout_with_auth(client):
    # Register and login
    client.post("/api/auth/register", json={
        "email": "buyer@test.com",
        "password": "pass123",
    })
    login_res = client.post("/api/auth/login", json={
        "email": "buyer@test.com",
        "password": "pass123",
    })
    token = login_res.json()["token"]

    # Mock stripe to avoid real API calls
    from unittest.mock import patch, MagicMock

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/test"

    with patch("stripe.checkout.Session.create", return_value=mock_session):
        res = client.post(
            "/api/billing/create-checkout",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert res.status_code == 200
    assert "url" in res.json()
```

**Step 2: Run test to verify it fails**

```bash
cd ~/Desktop/Work/price-compare/backend
python -m pytest tests/test_billing.py -v
# Expected: FAIL
```

**Step 3: Implement billing routes**

Create `backend/app/api/billing.py`:

```python
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.subscription import Subscription

stripe.api_key = settings.stripe_secret_key

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.post("/create-checkout")
def create_checkout(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        success_url=f"{settings.frontend_url}?checkout=success",
        cancel_url=f"{settings.frontend_url}?checkout=canceled",
        client_reference_id=user.id,
        customer_email=user.email,
    )
    return {"url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("client_reference_id")
        stripe_sub_id = session.get("subscription")

        if user_id and stripe_sub_id:
            subscription = Subscription(
                user_id=user_id,
                stripe_id=stripe_sub_id,
                status="active",
                plan="pro",
            )
            db.add(subscription)
            db.commit()

    elif event["type"] == "customer.subscription.deleted":
        sub_data = event["data"]["object"]
        subscription = (
            db.query(Subscription)
            .filter(Subscription.stripe_id == sub_data["id"])
            .first()
        )
        if subscription:
            subscription.status = "canceled"
            db.commit()

    return {"status": "ok"}
```

**Step 4: Register router in main.py**

Add to `backend/app/main.py`:

```python
from app.api.billing import router as billing_router

app.include_router(billing_router)
```

**Step 5: Run tests to verify they pass**

```bash
cd ~/Desktop/Work/price-compare/backend
python -m pytest tests/test_billing.py -v
# Expected: 2 passed
```

**Step 6: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add backend/
git commit -m "feat: add Stripe billing endpoints (checkout + webhook)"
```

---

## Phase 4: Frontend — UI

### Task 11: Routing and Layout

**Files:**
- Create: `frontend/src/components/Layout.tsx`
- Create: `frontend/src/pages/Home.tsx`
- Modify: `frontend/src/App.tsx`

**Step 1: Create Layout component**

Create `frontend/src/components/Layout.tsx`:

```tsx
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const token = localStorage.getItem("token");

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl flex items-center justify-between px-6 py-4">
          <Link to="/" className="text-xl font-bold text-slate-900">
            PriceScout
          </Link>
          {token ? (
            <Button
              variant="ghost"
              onClick={() => {
                localStorage.removeItem("token");
                window.location.reload();
              }}
            >
              Sign Out
            </Button>
          ) : (
            <Link to="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
          )}
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}
```

**Step 2: Create Home page**

Create `frontend/src/pages/Home.tsx`:

```tsx
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

interface HomeProps {
  onSearch: (query: string) => void;
  isSearching: boolean;
  searchesRemaining?: number;
}

const EXAMPLES = [
  "MacBook Pro M3 in Berlin",
  "Nike Air Max 90 in Seoul",
  "Canon R5 camera in New York",
  "2020 Omega Speedmaster in Tokyo",
];

export function Home({ onSearch, isSearching, searchesRemaining }: HomeProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <div className="flex flex-col items-center justify-center px-6 pt-32">
      <h1 className="text-5xl font-bold text-slate-900 mb-3">
        Find the Best Deal
      </h1>
      <p className="text-lg text-slate-500 mb-10">
        Anywhere in the World
      </p>

      <form onSubmit={handleSubmit} className="w-full max-w-xl flex gap-2">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What are you looking for? e.g. 2020 Omega Speedmaster in Tokyo"
          className="h-12 text-base"
          disabled={isSearching}
        />
        <Button type="submit" size="lg" disabled={isSearching || !query.trim()}>
          <Search className="w-4 h-4" />
        </Button>
      </form>

      <div className="mt-6 flex flex-wrap gap-2 justify-center">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => {
              setQuery(ex);
              onSearch(ex);
            }}
            className="text-sm text-slate-400 hover:text-slate-600 transition-colors"
            disabled={isSearching}
          >
            {ex}
          </button>
        ))}
      </div>

      {searchesRemaining !== undefined && searchesRemaining >= 0 && (
        <p className="mt-16 text-sm text-slate-400">
          {searchesRemaining} free search{searchesRemaining !== 1 ? "es" : ""} remaining
        </p>
      )}
    </div>
  );
}
```

**Step 3: Update App.tsx with routing**

Replace `frontend/src/App.tsx`:

```tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState } from "react";
import { Layout } from "@/components/Layout";
import { Home } from "@/pages/Home";

function App() {
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = (query: string) => {
    setIsSearching(true);
    // Will be connected to SSE hook in next task
    console.log("Searching:", query);
    setTimeout(() => setIsSearching(false), 2000);
  };

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route
            path="/"
            element={
              <Home onSearch={handleSearch} isSearching={isSearching} />
            }
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
```

**Step 4: Install lucide-react for icons**

```bash
cd ~/Desktop/Work/price-compare/frontend
npm install lucide-react
```

**Step 5: Verify it renders**

```bash
npm run dev
# Visit http://localhost:5173 → search page with centered input
```

**Step 6: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add frontend/
git commit -m "feat: add Layout, Home page with search bar and example queries"
```

---

### Task 12: useSearch Hook (SSE)

**Files:**
- Create: `frontend/src/hooks/useSearch.ts`
- Create: `frontend/src/types.ts`

**Step 1: Create shared types**

Create `frontend/src/types.ts`:

```typescript
export interface SearchResult {
  rank: number;
  product_name: string;
  price: string;
  currency: string;
  seller_name: string;
  seller_address: string;
  url: string;
  condition: string;
  notes: string;
}

export interface SearchResponse {
  product_understood: string;
  location: string;
  results: SearchResult[];
  search_summary: string;
}

export type SearchStatus = "idle" | "searching" | "analyzing" | "complete" | "error";

export interface SearchEvent {
  status: SearchStatus;
  message?: string;
  data?: SearchResponse;
}
```

**Step 2: Create the useSearch hook**

Create `frontend/src/hooks/useSearch.ts`:

```typescript
import { useState, useCallback } from "react";
import { SearchResponse, SearchStatus, SearchEvent } from "@/types";

export function useSearch() {
  const [status, setStatus] = useState<SearchStatus>("idle");
  const [message, setMessage] = useState("");
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (query: string) => {
    setStatus("searching");
    setMessage("Starting search...");
    setResults(null);
    setError(null);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch("/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ query }),
      });

      if (res.status === 402) {
        setStatus("error");
        setError("quota_exceeded");
        return;
      }

      if (!res.ok) {
        throw new Error("Search request failed");
      }

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No response stream");

      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const jsonStr = line.slice(6);
            try {
              const event: SearchEvent = JSON.parse(jsonStr);
              setStatus(event.status);
              if (event.message) setMessage(event.message);
              if (event.data) setResults(event.data);
            } catch {
              // skip malformed events
            }
          }
        }
      }
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }, []);

  const reset = useCallback(() => {
    setStatus("idle");
    setMessage("");
    setResults(null);
    setError(null);
  }, []);

  return { status, message, results, error, search, reset };
}
```

**Step 3: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add frontend/
git commit -m "feat: add useSearch hook with SSE stream parsing"
```

---

### Task 13: Results Page with Cards

**Files:**
- Create: `frontend/src/components/ResultCard.tsx`
- Create: `frontend/src/components/SearchProgress.tsx`
- Create: `frontend/src/pages/Results.tsx`
- Modify: `frontend/src/App.tsx`

**Step 1: Create SearchProgress component**

Create `frontend/src/components/SearchProgress.tsx`:

```tsx
import { SearchStatus } from "@/types";

interface SearchProgressProps {
  status: SearchStatus;
  message: string;
}

export function SearchProgress({ status, message }: SearchProgressProps) {
  const progress = status === "searching" ? 40 : status === "analyzing" ? 75 : 100;

  return (
    <div className="w-full max-w-xl mx-auto mt-16 px-6">
      <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-slate-900 rounded-full transition-all duration-700 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="mt-3 text-sm text-slate-500 text-center">{message}</p>
    </div>
  );
}
```

**Step 2: Create ResultCard component**

Create `frontend/src/components/ResultCard.tsx`:

```tsx
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ExternalLink } from "lucide-react";
import { SearchResult } from "@/types";

interface ResultCardProps {
  result: SearchResult;
}

const RANK_LABELS: Record<number, { label: string; color: string }> = {
  1: { label: "Best Price", color: "bg-yellow-100 text-yellow-800" },
  2: { label: "Runner Up", color: "bg-slate-100 text-slate-700" },
  3: { label: "Also Great", color: "bg-orange-50 text-orange-700" },
};

export function ResultCard({ result }: ResultCardProps) {
  const rank = RANK_LABELS[result.rank] || RANK_LABELS[3];

  return (
    <Card className="w-full">
      <CardContent className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <Badge className={rank.color} variant="secondary">
              {rank.label}
            </Badge>
            <h3 className="mt-2 text-lg font-semibold text-slate-900">
              {result.product_name}
            </h3>
            <p className="text-2xl font-bold text-slate-900 mt-1">
              {result.price}
            </p>
            <p className="text-sm text-slate-500 mt-2">
              {result.seller_name} &middot; {result.seller_address}
            </p>
            {result.condition && (
              <p className="text-sm text-slate-400 mt-1">
                Condition: {result.condition}
              </p>
            )}
            {result.notes && (
              <p className="text-sm text-slate-400 mt-1">{result.notes}</p>
            )}
          </div>
          <a href={result.url} target="_blank" rel="noopener noreferrer">
            <Button variant="outline" size="sm">
              View Deal <ExternalLink className="w-3 h-3 ml-1" />
            </Button>
          </a>
        </div>
      </CardContent>
    </Card>
  );
}
```

**Step 3: Create Results page**

Create `frontend/src/pages/Results.tsx`:

```tsx
import { Button } from "@/components/ui/button";
import { SearchProgress } from "@/components/SearchProgress";
import { ResultCard } from "@/components/ResultCard";
import { SearchResponse, SearchStatus } from "@/types";
import { RotateCcw } from "lucide-react";

interface ResultsProps {
  status: SearchStatus;
  message: string;
  results: SearchResponse | null;
  onNewSearch: () => void;
}

export function Results({ status, message, results, onNewSearch }: ResultsProps) {
  if (status === "searching" || status === "analyzing") {
    return <SearchProgress status={status} message={message} />;
  }

  if (!results || results.results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center pt-32 px-6">
        <p className="text-slate-500 text-lg">
          No results found. Try a different search.
        </p>
        <Button variant="outline" className="mt-6" onClick={onNewSearch}>
          <RotateCcw className="w-4 h-4 mr-2" /> New Search
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-6 pt-12 pb-16">
      <p className="text-sm text-slate-400 mb-1">
        {results.product_understood} in {results.location}
      </p>
      <div className="flex flex-col gap-4 mt-4">
        {results.results.map((result) => (
          <ResultCard key={result.rank} result={result} />
        ))}
      </div>
      <p className="text-sm text-slate-400 text-center mt-6">
        {results.search_summary}
      </p>
      <div className="flex justify-center mt-6">
        <Button variant="outline" onClick={onNewSearch}>
          <RotateCcw className="w-4 h-4 mr-2" /> New Search
        </Button>
      </div>
    </div>
  );
}
```

**Step 4: Wire up App.tsx with search flow**

Replace `frontend/src/App.tsx`:

```tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { Home } from "@/pages/Home";
import { Results } from "@/pages/Results";
import { useSearch } from "@/hooks/useSearch";

function App() {
  const { status, message, results, error, search, reset } = useSearch();
  const isSearching = status === "searching" || status === "analyzing";
  const showResults = status === "complete" || (isSearching && status !== "idle");

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route
            path="/"
            element={
              showResults ? (
                <Results
                  status={status}
                  message={message}
                  results={results}
                  onNewSearch={reset}
                />
              ) : (
                <Home onSearch={search} isSearching={isSearching} />
              )
            }
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
```

**Step 5: Verify it renders**

```bash
cd ~/Desktop/Work/price-compare/frontend
npm run dev
# Visit http://localhost:5173 → search page renders, clicking search shows progress
```

**Step 6: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add frontend/
git commit -m "feat: add Results page with ResultCard, SearchProgress, and full search flow"
```

---

### Task 14: Auth Pages (Login / Register)

**Files:**
- Create: `frontend/src/pages/Login.tsx`
- Create: `frontend/src/pages/Register.tsx`
- Modify: `frontend/src/App.tsx`

**Step 1: Create Login page**

Create `frontend/src/pages/Login.tsx`:

```tsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

export function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await apiFetch<{ token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      localStorage.setItem("token", res.token);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center pt-32 px-6">
      <Card className="w-full max-w-sm">
        <CardContent className="p-6">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Sign In</h2>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {error && <p className="text-sm text-red-500">{error}</p>}
            <Button type="submit" disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </Button>
          </form>
          <p className="text-sm text-slate-500 mt-4 text-center">
            No account?{" "}
            <Link to="/register" className="text-slate-900 underline">
              Register
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
```

**Step 2: Create Register page**

Create `frontend/src/pages/Register.tsx`:

```tsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

export function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      // Auto-login after register
      const res = await apiFetch<{ token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      localStorage.setItem("token", res.token);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center pt-32 px-6">
      <Card className="w-full max-w-sm">
        <CardContent className="p-6">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Create Account</h2>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              type="password"
              placeholder="Password (min 8 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              required
            />
            {error && <p className="text-sm text-red-500">{error}</p>}
            <Button type="submit" disabled={loading}>
              {loading ? "Creating account..." : "Create Account"}
            </Button>
          </form>
          <p className="text-sm text-slate-500 mt-4 text-center">
            Already have an account?{" "}
            <Link to="/login" className="text-slate-900 underline">
              Sign in
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
```

**Step 3: Add routes to App.tsx**

Add imports and routes:

```tsx
import { Login } from "@/pages/Login";
import { Register } from "@/pages/Register";

// Inside <Routes>:
<Route path="/login" element={<Login />} />
<Route path="/register" element={<Register />} />
```

**Step 4: Verify**

```bash
cd ~/Desktop/Work/price-compare/frontend
npm run dev
# Visit /login and /register pages
```

**Step 5: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add frontend/
git commit -m "feat: add Login and Register pages with JWT auth flow"
```

---

### Task 15: Paywall Modal

**Files:**
- Create: `frontend/src/components/PaywallModal.tsx`
- Modify: `frontend/src/App.tsx`

**Step 1: Install dialog component**

```bash
cd ~/Desktop/Work/price-compare/frontend
npx shadcn@latest add dialog
```

**Step 2: Create PaywallModal**

Create `frontend/src/components/PaywallModal.tsx`:

```tsx
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useState } from "react";

interface PaywallModalProps {
  open: boolean;
  onClose: () => void;
}

const FEATURES = [
  "Unlimited searches",
  "Priority agent speed",
  "Detailed price breakdowns",
];

export function PaywallModal({ open, onClose }: PaywallModalProps) {
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem("token");

  const handleSubscribe = async () => {
    if (!token) {
      window.location.href = "/register";
      return;
    }

    setLoading(true);
    try {
      const res = await apiFetch<{ url: string }>("/billing/create-checkout", {
        method: "POST",
      });
      window.location.href = res.url;
    } catch {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-center text-2xl">
            You've used your 3 free searches
          </DialogTitle>
          <DialogDescription className="text-center">
            Upgrade to Pro for unlimited access.
          </DialogDescription>
        </DialogHeader>
        <div className="border rounded-lg p-6 mt-4">
          <p className="text-center text-3xl font-bold text-slate-900">
            $9.99<span className="text-base font-normal text-slate-500">/month</span>
          </p>
          <ul className="mt-4 space-y-2">
            {FEATURES.map((f) => (
              <li key={f} className="flex items-center gap-2 text-sm text-slate-700">
                <Check className="w-4 h-4 text-green-600" /> {f}
              </li>
            ))}
          </ul>
          <Button
            className="w-full mt-6"
            onClick={handleSubscribe}
            disabled={loading}
          >
            {!token
              ? "Create Account to Subscribe"
              : loading
                ? "Redirecting..."
                : "Subscribe Now"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

**Step 3: Wire PaywallModal into App.tsx**

Add to App.tsx — show the modal when `error === "quota_exceeded"`:

```tsx
import { PaywallModal } from "@/components/PaywallModal";

// Inside the App component, add:
const showPaywall = error === "quota_exceeded";

// In the JSX, after </Routes>:
<PaywallModal open={showPaywall} onClose={reset} />
```

**Step 4: Verify**

```bash
npm run dev
# Paywall modal should appear when quota is exceeded
```

**Step 5: Commit**

```bash
cd ~/Desktop/Work/price-compare
git add frontend/
git commit -m "feat: add PaywallModal with Stripe checkout redirect"
```

---

## Phase 5: Polish & Integration

### Task 16: Backend — Run All Tests

**Step 1: Run the full backend test suite**

```bash
cd ~/Desktop/Work/price-compare/backend
python -m pytest tests/ -v
# Expected: All tests pass
```

**Step 2: Fix any failures**

If any tests fail, fix them now.

**Step 3: Commit any fixes**

```bash
cd ~/Desktop/Work/price-compare
git add backend/
git commit -m "fix: resolve test failures"
```

---

### Task 17: Frontend — Build Check

**Step 1: Run TypeScript type check and build**

```bash
cd ~/Desktop/Work/price-compare/frontend
npx tsc --noEmit
npm run build
# Expected: No errors, dist/ created
```

**Step 2: Fix any type errors or build failures**

If any issues, fix them now.

**Step 3: Commit any fixes**

```bash
cd ~/Desktop/Work/price-compare
git add frontend/
git commit -m "fix: resolve build errors"
```

---

### Task 18: End-to-End Smoke Test

**Step 1: Start all services**

```bash
# Terminal 1 — Postgres
cd ~/Desktop/Work/price-compare && docker compose up -d

# Terminal 2 — Backend
cd ~/Desktop/Work/price-compare/backend
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Terminal 3 — Frontend
cd ~/Desktop/Work/price-compare/frontend
npm run dev
```

**Step 2: Test the flow**

1. Visit `http://localhost:5173`
2. Type "Nike Air Max 90 in Berlin" and press Enter
3. Verify SSE progress updates appear
4. Verify 3 result cards render with prices, sellers, and links
5. Verify "View Deal" links open in new tabs

**Step 3: Test auth flow**

1. Click "Sign In" → go to `/register`
2. Create an account
3. Verify redirect to home
4. Search again — should work as authenticated user

**Step 4: Test quota (optional, manual)**

Set `FREE_SEARCH_LIMIT=1` in `.env`, restart backend, search twice — paywall should appear.

**Step 5: Final commit**

```bash
cd ~/Desktop/Work/price-compare
git add -A
git commit -m "chore: final integration polish"
```

---

## Summary

| Phase | Tasks | What's Built |
|-------|-------|-------------|
| 1: Scaffold | 1-3 | Backend (FastAPI), Frontend (Vite/React/Tailwind), Docker Compose |
| 2: DB & Auth | 4-7 | SQLAlchemy models, Alembic migrations, JWT auth, quota checking |
| 3: Agent & Search | 8-10 | Claude agent runner, SSE search endpoint, Stripe billing |
| 4: UI | 11-15 | Home page, Results with cards, Auth pages, Paywall modal |
| 5: Polish | 16-18 | Test suite, build verification, end-to-end smoke test |

**Total: 18 tasks, each 2-10 minutes. Estimated implementation: ~2-3 hours.**
