from services.LoggerService import LoggerService
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.types import ASGIApp
from services.SessionService import refresh_access_token

logger_service = LoggerService()

# Catch HTTP errors middleware and log
class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: ASGIApp
    ) -> ASGIApp:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger_service.error(request.url, e)
            message = e.args[0] if e is not None else "Internal server error"
            return JSONResponse(status_code=500, content={"message": f"{message}"})
        
# Add JWT to the headers response
class AddJWTToResponseMiddleware(BaseHTTPMiddleware):  
    def __init__(self, app, excluded_paths):
        super().__init__(app)
        self.excluded_paths = excluded_paths
    async def dispatch(
        self, request: Request, call_next: ASGIApp
    ) -> ASGIApp:
        if not any(request.url.path.startswith(path) for path in self.excluded_paths):
            try:
                response = await call_next(request)
                authorization = request.headers.get("Authorization")
                if authorization:
                    if authorization.startswith("Bearer "):
                        jwt = authorization.replace("Bearer ", "")
                        refreshed_jwt = refresh_access_token(jwt)
                        response.headers["Authorization"] = f"Bearer {refreshed_jwt}"
                        return response
                    
                return await call_next(request)
            except Exception as e:
                logger_service.error(request.url, e)
                return JSONResponse(status_code=500, content={"message": "Internal server error"})
        else:
            return await call_next(request)
        
# Catch Requests validation errors and log
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger_service.error(request.url, f"Validation request error: {exc}")
    return JSONResponse(status_code=422, content={"detail": str(exc)})