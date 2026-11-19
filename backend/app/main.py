from fastapi import FastAPI

from app.core.config import settings
from app.core.database import check_connection

app = FastAPI(title=settings.app_name)


@app.get("/")
def root():
    return {"message": "RepoPilot is running", "app": settings.app_name}


@app.get("/health")
def health():
    db_ok = check_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "db": "connected" if db_ok else "disconnected",
    }