from app.data.user_in_db import UserInDB
from app.dependencies import database

user_collection = database.user

class UserRepository:
    @staticmethod
    async def get_user_by_username(username: str):
        return await user_collection.find_one({"username": username})
    @staticmethod
    async def insert_user(user: UserInDB):
        return await user_collection.insert_one(user.model_dump())
