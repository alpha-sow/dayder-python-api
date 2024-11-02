from pydantic import BaseModel

from app.data.database import user_collection


class User(BaseModel):
    id: str
    username: str
    email: str | None = None
    full_name: str | None = None
    hashed_password: str
    disabled: bool | None = None


class UserRepository:
    @staticmethod
    async def get_user_by_username(username: str):
        return await user_collection.find_one({"username": username})
