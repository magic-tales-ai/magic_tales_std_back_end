from typing import List
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from services.logger_service import LoggerService
from services.session_service import refresh_access_token

logger_service = LoggerService()


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch unhandled exceptions and log them, returning a standardized error response.

    Attributes:
        app (ASGIApp): The next ASGI application to call.
    """

    async def dispatch(self, request: Request, call_next: ASGIApp) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"message": e.detail})
        except Exception as e:
            logger_service.error(f"Unhandled exception for {request.url}: {e}")
            message = str(e.args[0]) if e.args else "Internal server error"
            return JSONResponse(status_code=500, content={"message": message})


class AddJWTToResponseMiddleware(BaseHTTPMiddleware):
    """
    Middleware to refresh JWT tokens in the response headers, if applicable.

    Attributes:
        app (ASGIApp): The next ASGI application to call.
        excluded_paths (List[str]): Paths to exclude from JWT refresh logic.
    """

    def __init__(self, app: ASGIApp, excluded_paths: List[str]):
        super().__init__(app)
        self.excluded_paths = excluded_paths

    async def dispatch(self, request: Request, call_next: ASGIApp) -> Response:
        response = await call_next(request)
        if not any(request.url.path.startswith(path) for path in self.excluded_paths):
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                jwt = authorization[7:]
                refreshed_jwt = refresh_access_token(
                    jwt
                )  # Ensure this is an async function if performing I/O
                response.headers["Authorization"] = f"Bearer {refreshed_jwt}"
        return response


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    ASGI handler for request validation exceptions, logging the error and returning a 422 response.

    Args:
        request (Request): The request object.
        exc (RequestValidationError): The validation exception encountered.

    Returns:
        JSONResponse: A standardized error response indicating the validation failure.
    """
    logger_service.error(f"Validation error for {request.url}: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
