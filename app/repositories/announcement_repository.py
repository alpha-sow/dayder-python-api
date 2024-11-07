from bson import ObjectId

from app.data import Announcement
from app.dependencies import database

announcement_collection = database.announcement

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
    @staticmethod
    async def put_one(announcement: Announcement):
        return await announcement_collection.insert_one(announcement.model_dump())