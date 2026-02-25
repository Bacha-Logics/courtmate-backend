from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import SessionLocal
from app.services.reminder_delivery import process_due_reminders


# ============================================================
# Scheduler Setup
# ============================================================

scheduler = BackgroundScheduler()


def reminder_job():
    """
    Runs every minute to process due reminders.
    Safe DB session handling.
    """
    db = SessionLocal()
    try:
        processed = process_due_reminders(db)
        if processed:
            print(f"[Reminder Job] Processed {processed} reminders")
    except Exception as e:
        print("Reminder job error:", e)
    finally:
        db.close()


# ============================================================
# Lifespan (Startup / Shutdown)
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    if not scheduler.running:
        scheduler.add_job(
            reminder_job,
            "interval",
            minutes=1,
            id="reminder_job",
            replace_existing=True,
        )
        scheduler.start()
        print("✅ Reminder scheduler started")

    yield

    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Reminder scheduler stopped")


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None if settings.ENV == "production" else "/docs",
    redoc_url=None,
)

# ============================================================
# CORS (FIXED FOR VERCEL + LOCALHOST)
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Routers
# ============================================================

app.include_router(api_router, prefix="/api/v1")

# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENV
    }