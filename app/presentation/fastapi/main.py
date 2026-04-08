from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from contextlib import asynccontextmanager

from app.infrastructure.config.config import get_settings
from app.infrastructure.logging.setup import configure_logging
from app.infrastructure.logging.adapter import get_logger
from app.presentation.fastapi.middleware.exception import ExceptionMiddleware
from app.presentation.fastapi.middleware.request_id import RequestIdMiddleware

config = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("broker started")
    yield 
    
    logger.info("broker stoped")
    

def create_application() -> FastAPI:
    _app = FastAPI(
        title=config.PROJECT_TITLE,
        description=config.PROJECT_DESCRIPTION,
        lifespan=lifespan,
        docs_url=f"{config.BASE_PATH}docs",
        # root_path=config.BASE_PATH,
        openapi_url=f"{config.BASE_PATH}openapi.json"
    )

    _app.add_middleware(ExceptionMiddleware, logger=get_logger("exception_middleware"))
    _app.add_middleware(RequestIdMiddleware)
    return _app

app = create_application()

@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    return {"status": "ready"}


Instrumentator().instrument(app).expose(app)