from fastapi import FastAPI

from app.routers import announcements, users

app = FastAPI(
    title="DAYDER",
    version="1.0.0",
)

app.include_router(
    users.router,
    tags=["users"],
)
app.include_router(
    announcements.router,
    prefix="/announcements",
    tags=['announcements'],
)