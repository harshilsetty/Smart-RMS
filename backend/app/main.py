from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.v1.endpoints import rms, analytics, knowledge, evaluation, departments, users, nlp, active_learning, models
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
    
    # Environment validation (PART 3)
    if settings.ENVIRONMENT == "production":
        if settings.INTEGRATION_MODE == "mock":
            print("[!] WARNING: Running in production with MOCK integration.")
        if settings.AI_PROVIDER == "mock":
            print("[!] WARNING: Running in production with MOCK AI provider.")
        # Ensure fail fast if integration isn't mock and credentials missing (example)
        if settings.INTEGRATION_MODE == "lpu" and not settings.GEMINI_API_KEY:
            raise RuntimeError("CRITICAL ERROR: LPU Integration mode requires valid API keys.")
            
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
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@app.get("/ready", tags=["Health"])
def readiness_check():
    # PART 10 - Readiness Check
    # In a real scenario, this checks DB/Cache connectivity.
    # Here we check if the mock adapters are successfully loaded.
    is_ready = True
    if settings.INTEGRATION_MODE == "lpu":
        # Simulate fail if LPU adapter isn't fully implemented
        is_ready = False
        
    if not is_ready:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Service Unavailable: Integration layer not ready")
        
    return {"status": "ready", "integration": settings.INTEGRATION_MODE}

# Mount API Routers
app.include_router(rms.router, prefix="/api/v1/rms", tags=["RMS Tickets"])
app.include_router(departments.router, prefix="/api/v1/departments", tags=["Departments"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Staff Users"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Operations Analytics"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["Knowledge Base"])
app.include_router(nlp.router, prefix="/api/v1/nlp", tags=["NLP Intelligence"])
app.include_router(evaluation.router, prefix="/api/v1/evaluation", tags=["Evaluation"])
app.include_router(active_learning.router, prefix="/api/v1/active-learning", tags=["Active Learning Queue"])
app.include_router(models.router, prefix="/api/v1/models", tags=["Model Registry"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
