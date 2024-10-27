from fastapi import FastAPI

from app.routers import announcement_router

app = FastAPI(
    title="DAYDER",
    version="1.0.0",
)

app.include_router(announcement_router.router)