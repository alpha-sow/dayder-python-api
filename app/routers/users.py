from typing import Annotated
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from passlib.context import CryptContext
from pymongo.synchronous.collection import Collection
from starlette.status import HTTP_201_CREATED
from app.data import User, UserInDB, NewUserInDB
from app.dependencies import database, oauth2_scheme
from app.settings import settings
from app.logger import logger
from fastapi_pagination.ext.motor import paginate as motor_paginate


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


def get_collection_user() -> Collection:
    """
    Retrieves the user collection from the database.
    """
    return database.user

def get_password_hash(password) -> str:
    """
    Hashes the password using bcrypt.
    """
    return pwd_context.hash(password)

@router.get("")
async def read_users(token: Annotated[str, Depends(oauth2_scheme)],
) -> Page[User]:
    """
    Retrieves all users from the database.
    Requires authentication via token.
    """
    return await motor_paginate(get_collection_user())

@router.post("", status_code=HTTP_201_CREATED)
async def create_user(user: NewUserInDB, token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """
    Creates a new user with hashed password.
    Requires authentication via token.
    """
    new_user = UserInDB(hashed_password=get_password_hash(user.password), **user.model_dump())
    await  get_collection_user().insert_one(new_user.model_dump())
    return User(**new_user.model_dump())

@router.get("/{id}")
async def read_user(id: str, token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """
    Retrieves a user by ID.
    Requires authentication via token.
    """
    user = await get_collection_user().find_one({"_id": ObjectId(id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

async def create_default_admin() -> None:
    """
    Creates a default admin user on application startup.
    Uses ADMIN_USERNAME and ADMIN_PASSWORD from environment variables,
    or defaults to 'admin'/'admin123' for development.
    """
    try:
        admin_username = settings.ADMIN_USERNAME
        admin_password = settings.ADMIN_PASSWORD
        
        collection = get_collection_user()
        existing_admin = await collection.find_one(filter={"username": admin_username})
        
        if existing_admin is not None:
            logger.info(f"Default admin user '{admin_username}' already exists. Skipping creation.")
            return
        
        new_admin = UserInDB(
            username=admin_username,
            full_name="Administrator",
            email="admin@dayder.com",
            hashed_password=get_password_hash(admin_password),
            disabled=False
        )
        
        await collection.insert_one(new_admin.model_dump())
        
        if admin_password == "admin123":
            logger.warning(f"Default admin user '{admin_username}' created with default password 'admin123'. Please change this in production!")
        else:
            logger.info(f"Default admin user '{admin_username}' created successfully.")
        
    except Exception as e:
        logger.error(f"Failed to create default admin user: {str(e)}")
