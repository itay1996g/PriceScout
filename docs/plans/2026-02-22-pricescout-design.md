# PriceScout - Location-Based Price Comparison SaaS

**Date:** 2026-02-22
**Status:** Approved

## Overview

PriceScout is a SaaS app that lets users find the best deals on any product in any location using natural language. An AI agent (Claude) handles all web research — no custom scrapers needed.

**Example query:** "2020 Omega Speedmaster watch in Tokyo"
**Result:** Top 3 offers ranked by price, with seller details and links.

## Requirements

- Natural language product + location search
- AI agent (Claude) with web_search and web_fetch tools does all research
- User types the location (no GPS requirement)
- Returns top 3 offers ranked by price and proximity
- 3 free searches, then paid subscription ($9.99/month via Stripe)
- Real-time only — no search history or caching
- Minimal & modern UI (shadcn/ui, Tailwind)

## Architecture

**Approach: Synchronous + SSE streaming**

```
React (Vite) → FastAPI → Claude Agent (web_search, web_fetch) → Structured JSON → SSE stream → Result cards
```

- Frontend sends query to `/api/search`
- Backend invokes Claude agent with tools
- Agent searches the web, fetches listings, extracts structured data
- Progress streamed via Server-Sent Events
- Final results returned as structured JSON

No queue infrastructure. No background workers. Simple request → agent → streamed response.

## Agent Design

### Tools

| Tool | Purpose |
|------|---------|
| `web_search` | Search for product listings in the specified location |
| `web_fetch` | Fetch product pages to extract price, seller, address |

### Agent Workflow

1. Parse query → understand product and location
2. Run 2-3 targeted web searches
3. Fetch most promising result pages
4. Extract structured data (product, price, seller, location, URL, condition)
5. Rank by price (primary), reputation/proximity (secondary)
6. Return top 3 as structured JSON

### Output Schema

```json
{
  "product_understood": "2020 Omega Speedmaster Professional",
  "location": "Tokyo, Japan",
  "results": [
    {
      "rank": 1,
      "product_name": "Omega Speedmaster Professional 2020",
      "price": "$4,200",
      "currency": "USD",
      "seller_name": "Jackroad Watch Shop",
      "seller_address": "3-26-6 Nishi-Shinjuku, Tokyo",
      "url": "https://...",
      "condition": "Pre-owned, Excellent",
      "notes": "Includes box and papers"
    }
  ],
  "search_summary": "Found 8 listings across 4 shops in Tokyo. Top 3 selected by price."
}
```

### SSE Progress Events

```json
{"status": "searching", "message": "Searching for Omega Speedmaster in Tokyo..."}
{"status": "analyzing", "message": "Analyzing 8 listings from 4 sellers..."}
{"status": "complete", "data": { ... }}
```

## UI/UX Design

Three screens, minimal & modern.

### Screen 1: Home / Search
- Centered search bar with placeholder examples
- Free search counter at bottom
- Clean gradient or solid background

### Screen 2: Results
- Progress bar with agent status during loading
- 3 result cards with visual hierarchy (gold/silver/bronze badges)
- Each card: product name, price (local + USD), seller, location, condition
- "View Deal" links to original listing
- Search summary at bottom

### Screen 3: Paywall
- Shown when 3 free searches exhausted
- Single Pro plan card ($9.99/month)
- Feature list + Stripe checkout button

### Design System
- shadcn/ui components (Radix primitives)
- TailwindCSS styling
- Neutral palette: white/slate, dark text, accent CTA color

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/search` | Submit search, returns SSE stream |
| `POST` | `/api/auth/register` | Create account |
| `POST` | `/api/auth/login` | Login, returns JWT |
| `GET` | `/api/auth/me` | Current user + remaining searches |
| `POST` | `/api/billing/create-checkout` | Stripe checkout session |
| `POST` | `/api/billing/webhook` | Stripe webhook handler |

## Auth & Billing

- **Anonymous:** 3 searches tracked by session cookie
- **Registered:** Email + password (bcrypt), JWT tokens, 3 free searches
- **Subscribers:** Unlimited, synced via Stripe webhooks

## Database Schema

```sql
users (id UUID PK, email VARCHAR UNIQUE, password VARCHAR, created_at TIMESTAMP)
subscriptions (id UUID PK, user_id UUID FK, stripe_id VARCHAR UNIQUE, status VARCHAR, plan VARCHAR, current_period_end TIMESTAMP)
search_usage (id UUID PK, user_id UUID NULLABLE, session_id VARCHAR, searched_at TIMESTAMP)
```

Quota check: count `search_usage` rows for user/session. If >= 3 and no active subscription → paywall.

## Tech Stack

### Backend (Python)
- FastAPI + uvicorn
- anthropic (Claude SDK)
- SQLAlchemy + Alembic (ORM + migrations)
- stripe (billing)
- PyJWT + bcrypt (auth)
- sse-starlette (Server-Sent Events)

### Frontend (TypeScript)
- React + Vite
- TailwindCSS + shadcn/ui
- Custom hooks: useSearch (SSE), useAuth, useSubscription

## Project Structure

```
pricescout/
├── frontend/
│   ├── src/
│   │   ├── components/     # SearchBar, ResultCard, PaywallModal, Layout
│   │   ├── pages/          # Home, Results
│   │   ├── hooks/          # useSearch, useAuth, useSubscription
│   │   ├── lib/            # API client, auth helpers
│   │   └── App.tsx
│   ├── tailwind.config.ts
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI app + CORS
│   │   ├── api/
│   │   │   ├── search.py   # /search endpoint (SSE)
│   │   │   ├── auth.py     # register, login, me
│   │   │   └── billing.py  # Stripe checkout + webhook
│   │   ├── agent/
│   │   │   ├── runner.py   # Claude agent orchestration
│   │   │   └── prompts.py  # System prompt + tool configs
│   │   ├── models/         # SQLAlchemy models
│   │   ├── db.py           # DB connection
│   │   └── config.py       # Settings
│   ├── requirements.txt
│   └── alembic/            # DB migrations
├── docker-compose.yml      # Local dev (Postgres)
└── README.md
```

## Deployment

- **Frontend:** Vercel
- **Backend:** Railway or Fly.io
- **Database:** Managed Postgres (via hosting platform)
- **Stripe:** Test mode for dev, live for prod
