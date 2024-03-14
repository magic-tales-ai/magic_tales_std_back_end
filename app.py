from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables before db.py

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from middlewares import (
    AddJWTToResponseMiddleware,
    ErrorHandlerMiddleware,
    validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError

from controllers.session_controller import session_router
from controllers.profile_controller import profile_router
from controllers.story_controller import story_router
from controllers.plan_controller import plan_router
from controllers.user_controller import user_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(session_router)
app.include_router(profile_router)
app.include_router(story_router)
app.include_router(plan_router)
app.include_router(user_router)

# Middlewares
EXCLUDED_PATHS = [
    "/session/login",
    "/session/register",
    "/session/login-swagger",
    "/docs",
    "/openapi.json",
    "/static",
]
app.add_middleware(AddJWTToResponseMiddleware, excluded_paths=EXCLUDED_PATHS)
app.add_middleware(ErrorHandlerMiddleware)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

static_folder = os.getenv("STATIC_FOLDER")
app.mount(static_folder, StaticFiles(directory=static_folder), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=os.getenv("SERVER_HOST"),
        port=int(os.getenv("SERVER_PORT")),
        reload=True,
    )
