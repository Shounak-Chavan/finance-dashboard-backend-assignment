import time
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.logging_config import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        logger.info(
            f"{request.method} {request.url.path} "
            f"{response.status_code} {duration:.4f}s"
        )

        return response