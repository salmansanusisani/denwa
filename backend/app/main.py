import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import companies, documents, calls, webhooks
from app.config import WORKER_ENABLED

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("denwa.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ensure tables exist.
    from app.db.database import init_db

    init_db()

    # 2. Rebuild the in-memory RAG index from persisted chunk rows so knowledge
    #    uploaded in a previous run is still retrievable.
    try:
        import app.db.database as database_module
        from app.rag.ingest import rehydrate_index

        with database_module.SessionLocal() as session:
            rehydrate_index(session)
    except Exception as exc:  # pragma: no cover - startup must not crash on optional index
        logger.warning("Could not rehydrate RAG index: %s", exc)

    # 3. Start the persistent callback worker as a background task.
    worker_task: Optional[asyncio.Task] = None
    if WORKER_ENABLED:
        from app.worker.callback_worker import run_worker_loop

        worker_task = asyncio.create_task(run_worker_loop())
        logger.info("Denwa callback worker started (WORKER_ENABLED=%s)", WORKER_ENABLED)

    yield

    if worker_task is not None:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="Denwa API", lifespan=lifespan)

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


@app.get("/health")
def health():
    return {"status": "ok"}