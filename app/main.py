from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_pagination import add_pagination

from app.routers import announcements, users, auth

@asynccontextmanager
async def lifespan(_: FastAPI):
    await users.create_default_admin()
    yield

app = FastAPI(
    title="DAYDER",
    version="0.2.0",
    description="DAYDER API",
    lifespan=lifespan,
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)

app.include_router(
    announcements.router,
    prefix="/announcements",
    tags=['announcements'],
)

add_pagination(app)
