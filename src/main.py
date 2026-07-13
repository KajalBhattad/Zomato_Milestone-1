import logging
from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Request, status
# pyrefly: ignore [missing-import]
from fastapi.responses import JSONResponse, HTMLResponse
# pyrefly: ignore [missing-import]
from fastapi.exceptions import RequestValidationError
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

@app.get("/", response_class=HTMLResponse)
def read_index():
    """
    Serves the user-facing HTML recommendation dashboard.
    """
    import os
    static_file_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    try:
        with open(static_file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Zomato AI Dashboard under construction</h1><p>Please check backend static file setup.</p>",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

