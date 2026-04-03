import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from backend.core.config import settings
from backend.core.exceptions import register_exception_handlers
from backend.core.logging_config import setup_logging
from backend.core.rate_limiter import limiter
from backend.db.session import init_db

from backend.api.routes import auth_routes, user_routes, finance_routes, summary_routes
from backend.api.middleware.request_logger import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🚫 Skip init_db during tests
    if os.getenv("TESTING") != "1":
        await init_db()
    yield


def create_app() -> FastAPI:
    # setup logging first
    setup_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # change in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate Limiting (SlowAPI)
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )

    # Request Logging Middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Global Exception Handlers
    register_exception_handlers(app)

    #  Routers
    app.include_router(auth_routes.router)
    app.include_router(user_routes.router)
    app.include_router(finance_routes.router)
    app.include_router(summary_routes.router)

    # Health Check
    @app.get("/")
    async def root():
        return {"message": f"{settings.APP_NAME} is running"}

    return app


app = create_app()