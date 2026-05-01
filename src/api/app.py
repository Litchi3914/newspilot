from fastapi import FastAPI
import os

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes.health import router as health_router
from src.api.routes.review import router as review_router
from src.api.middleware.request_id import RequestIDMiddleware
from src.api.middleware.error_handler import unhandled_exception_handler


# Load project .env on app startup so local run can use real LLM config.
load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(
        title='NewsPilot Review API',
        version='0.1.0',
        description='AI-powered review API for HZAU news drafts.',
    )
    cors_origins = os.getenv(
        'CORS_ORIGINS',
        'http://localhost:5173,https://litchi3914.github.io',
    ).split(',')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in cors_origins if origin.strip()],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.add_middleware(RequestIDMiddleware)
    app.include_router(health_router)
    app.include_router(review_router, prefix='/api/v1')
    app.add_exception_handler(Exception, unhandled_exception_handler)
    return app


app = create_app()
