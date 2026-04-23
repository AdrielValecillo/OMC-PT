from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import leads_router
from app.core import get_settings
from app.db.database import create_tables

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.db_auto_create:
        create_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.include_router(leads_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "OMC Leads API activa"}
