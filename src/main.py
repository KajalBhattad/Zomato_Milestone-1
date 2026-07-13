import logging
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan logic to handle startup initialization of the cached dataset.
    """
    logger.info("Initializing restaurant database cache on application startup...")
    try:
        initialize_cache()
        logger.info("Restaurant database cache initialized successfully.")
    except Exception as e:
        logger.critical(f"CRITICAL ERROR: Failed to load dataset at startup: {e}")
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
