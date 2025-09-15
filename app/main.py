from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_pagination import add_pagination

from app.routers import announcements, authentication, users

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
    authentication.router,
    prefix="/api/authentication",
    tags=["authentication"],
)

app.include_router(
    users.router,
    prefix="/api/users",
    tags=["users"],
)

app.include_router(
    announcements.router,
    prefix="/api/announcements",
    tags=['announcements'],
)

add_pagination(app)
