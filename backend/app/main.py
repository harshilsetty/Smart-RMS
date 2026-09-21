from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.v1.endpoints import rms, analytics, knowledge
from app.schemas.rms import HealthResponse

import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logging
    print("==================================================")
    print(">>> SMART RMS - University Copilot API Started")
    print(f"[*] Environment: {settings.ENVIRONMENT}")
    print(f"[*] AI Provider: {settings.AI_PROVIDER}")
    print(f"[*] Vector Store: {settings.VECTOR_STORE_TYPE}")
    print(f"[*] Integration: {settings.INTEGRATION_MODE}")
    print("==================================================")
    yield
    print("[*] SMART RMS API Shutting down gracefully.")

app = FastAPI(
    title="Smart RMS - University Resolution & Operations API",
    description="AI-assisted RMS resolution and operations platform for universities using NLP, RAG, and human-in-the-loop workflows.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root Health Check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return HealthResponse(
        status="healthy",
        service="Smart RMS Backend API",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        ai_provider=settings.AI_PROVIDER,
        vector_store=settings.VECTOR_STORE_TYPE,
        mock_mode=(settings.AI_PROVIDER == "mock"),
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

# Mount API Routers
app.include_router(rms.router, prefix="/api/v1/rms", tags=["RMS Tickets"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Operations Analytics"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["Knowledge Base"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
