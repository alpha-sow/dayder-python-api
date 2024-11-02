from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from .database import announcement_collection


class Announcement(BaseModel):
    id:  str | None = None
    title: str = Field(...)
    description: str = Field(...)
    thumbnail: str | None = None
    createdAt: Optional[datetime] = Field(default_factory=datetime.now)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.now)

class AnnouncementRepository:
    @staticmethod
    async def find_all():
        return await announcement_collection.find().to_list()
    @staticmethod
    async def insert_one(announcement: Announcement):
        return await announcement_collection.insert_one(announcement.model_dump())
    @staticmethod
    async def find_one(announcement_id: str):
        return await announcement_collection.find_one({"_id": ObjectId(announcement_id)})
    @staticmethod
    async def delete_one(announcement_id: str):
        return await announcement_collection.delete_one({"_id": ObjectId(announcement_id)})