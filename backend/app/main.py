from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import companies, documents, calls, webhooks
from app.db.database import init_db

app = FastAPI(title="Denwa API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Direct root routes
app.include_router(companies.router)
app.include_router(documents.router)
app.include_router(calls.router)
app.include_router(calls.internal_router)
app.include_router(webhooks.router)

# /api/v1 compatibility routes for frontend
api_v1 = "/api/v1"
app.include_router(companies.router, prefix=api_v1)
app.include_router(documents.router, prefix=api_v1)
app.include_router(calls.router, prefix=api_v1)
app.include_router(calls.internal_router, prefix=api_v1)
app.include_router(webhooks.router, prefix=api_v1)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
