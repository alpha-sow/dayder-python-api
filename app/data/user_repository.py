from pydantic import BaseModel

from app.data.database import user_collection


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str

class NewUserInDB(User):
    password: str


class UserRepository:
    @staticmethod
    async def get_user_by_username(username: str):
        return await user_collection.find_one({"username": username})
    @staticmethod
    async def insert_user(user: UserInDB):
        return await user_collection.insert_one(user.model_dump())
