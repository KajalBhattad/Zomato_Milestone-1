import logging
import threading
from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Request, status
# pyrefly: ignore [missing-import]
from fastapi.responses import JSONResponse
# pyrefly: ignore [missing-import]
from fastapi.exceptions import RequestValidationError
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router as api_router
from src.data.cache import initialize_cache

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def _load_cache_background():
    """
    Loads the dataset cache in a background thread so startup is not blocked.
    Railway has strict startup timeouts — loading a large HuggingFace dataset
    synchronously can exceed this limit and cause crash loops.
    The /api/v1/health and /api/v1/recommend endpoints gracefully handle the
    'cache not yet ready' state via is_cache_initialized() checks.
    """
    logger.info("Background thread: starting dataset cache initialization...")
    try:
        initialize_cache()
        logger.info("Background thread: dataset cache initialized successfully.")
    except Exception as e:
        logger.critical(f"Background thread: CRITICAL ERROR loading dataset: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan: kicks off dataset loading in a background thread so
    the server binds its port immediately (satisfying Railway's health check),
    while the dataset continues loading asynchronously.
    """
    logger.info("Application startup: launching background cache loader...")
    thread = threading.Thread(target=_load_cache_background, daemon=True)
    thread.start()
    yield

app = FastAPI(
    title="Zomato Restaurant Recommendation Service",
    description="AI-powered recommendation system combining local filters and Groq LLM ranking.",
    version="1.0.0",
    lifespan=lifespan
)

# Allow cross-origin requests from the Vercel-hosted frontend.
# Replace the placeholder URL with your actual Vercel deployment URL after deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",          # Local development
        "http://localhost:5500",          # Live Server (VS Code)
        "https://your-app.vercel.app",   # TODO: Replace with your actual Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom handler to translate Pydantic/FastAPI validation exceptions to 400 Bad Requests
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Request validation failed: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()}
    )

# Include API endpoints router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    """
    Root health/info endpoint. Frontend is served separately on Vercel.
    """
    return {
        "service": "Zomato Restaurant Recommendation API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
