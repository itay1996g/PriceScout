from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.auth import router as auth_router
from app.api.search import router as search_router
from app.api.billing import router as billing_router

app = FastAPI(title="PriceScout API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(search_router)
app.include_router(billing_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
