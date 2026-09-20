from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import Base, engine
import app.models # Ensure all models are registered

# Automatic schema creation is permitted only for local/demo use. Production uses Alembic migrations.
if settings.AUTO_CREATE_SCHEMA:
    Base.metadata.create_all(bind=engine)
from app.core.logging import RequestIDMiddleware, logger
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.family import router as family_router
from app.api.v1.verification import router as verification_router
from app.api.v1.schemes import router as schemes_router
from app.api.v1.documents import router as documents_router
from app.api.v1.eligibility import router as eligibility_router
from app.api.v1.applications import router as applications_router
from app.api.v1.duplicates import router as duplicates_router
from app.api.v1.life_events import router as life_events_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.chatbot import router as chatbot_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Request ID Middleware
app.add_middleware(RequestIDMiddleware)

# CORS Middleware
origins = settings.ALLOWED_ORIGINS
if isinstance(origins, str):
    origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(auth_router, prefix=settings.API_V1_STR, tags=["Authentication"])
app.include_router(family_router, prefix=settings.API_V1_STR, tags=["Family Management"])
app.include_router(verification_router, prefix=settings.API_V1_STR, tags=["Member Verification"])
app.include_router(schemes_router, prefix=settings.API_V1_STR, tags=["Scheme Catalog"])
app.include_router(documents_router, prefix=settings.API_V1_STR, tags=["Document Vault"])
app.include_router(eligibility_router, prefix=settings.API_V1_STR, tags=["Eligibility Engine & Officer Queue"])
app.include_router(applications_router, prefix=settings.API_V1_STR, tags=["Scheme Applications"])
app.include_router(duplicates_router, prefix=settings.API_V1_STR, tags=["Duplicate Resolution"])
app.include_router(life_events_router, prefix=settings.API_V1_STR, tags=["Life Events & Family Lineage Engine"])
app.include_router(analytics_router, prefix=settings.API_V1_STR, tags=["State Analytics Dashboard"])
app.include_router(chatbot_router, prefix=settings.API_V1_STR, tags=["AI Welfare Assistant Chatbot"])




@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API v{settings.VERSION}",
        "docs": f"{settings.API_V1_STR}/docs",
        "health": f"{settings.API_V1_STR}/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
