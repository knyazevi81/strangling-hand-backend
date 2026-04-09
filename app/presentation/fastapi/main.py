from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from contextlib import asynccontextmanager

from app.infrastructure.config.config import get_settings
from app.infrastructure.logging.setup import configure_logging
from app.infrastructure.logging.adapter import get_logger
from app.presentation.fastapi.middleware.exception import ExceptionMiddleware
from app.presentation.fastapi.middleware.request_id import RequestIdMiddleware
from app.presentation.fastapi.routers.auth import router as auth_router
from app.presentation.fastapi.routers.users import router as users_router
from app.presentation.fastapi.routers.subscribes import router as subscribes_router
from app.presentation.fastapi.routers.free_vpn import router as free_vpn_router

config = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("savebit started")
    yield
    logger.info("savebit stopped")


def create_application() -> FastAPI:
    _app = FastAPI(
        title=config.PROJECT_TITLE,
        description=config.PROJECT_DESCRIPTION,
        lifespan=lifespan,
        docs_url=f"{config.BASE_PATH}docs",
        openapi_url=f"{config.BASE_PATH}openapi.json",
    )

    _app.add_middleware(ExceptionMiddleware, logger=get_logger("exception_middleware"))
    _app.add_middleware(RequestIdMiddleware)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _app.include_router(auth_router, prefix="/api/v1")
    _app.include_router(users_router, prefix="/api/v1")
    _app.include_router(subscribes_router, prefix="/api/v1")
    _app.include_router(free_vpn_router, prefix="/api/v1")

    return _app


app = create_application()


@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    return {"status": "ready"}


Instrumentator().instrument(app).expose(app)
