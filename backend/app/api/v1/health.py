import time
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import get_db

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    project: str
    version: str
    environment: str
    demo_mode: bool
    database: str
    timestamp: float


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENV,
        demo_mode=settings.DEMO_MODE,
        database=db_status,
        timestamp=time.time(),
    )
