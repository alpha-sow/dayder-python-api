from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from passlib.context import CryptContext
from pymongo.synchronous.collection import Collection
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_201_CREATED

from app.data import User, UserInDB, TokenData, Token, NewUserInDB
from app.dependencies import database, oauth2_scheme
from app.settings import settings
from app.logger import logger



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


def get_collection_user() -> Collection:
    """
    Retrieves the user collection from the database.
    """
    return database.user


def verify_password(plain_password, hashed_password) -> bool:
    """
    Verifies a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    """
    Hashes the password using bcrypt.
    """
    return pwd_context.hash(password)


async def get_user(username: str, collection: Collection) -> dict | None:
    """
    Retrieves a user by username.
    """
    return await collection.find_one(filter={"username": username})


async def authenticate_user(username: str, password: str, collection: Collection) -> User | None:
    """
    Authenticates the user and returns a User object if successful.
    """
    response = await get_user(username, collection)
    if response is None:
        return None
    user = UserInDB(**response)
    if user.disabled:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Creates a JWT token with an expiration time.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.post("/token")
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    Authenticates the user and returns a JWT token if successful.
    Raises HTTP 401 if authentication fails.
    """
    user = await authenticate_user(form_data.username, form_data.password, get_collection_user())
    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


def get_token_data(token: str, http_exception: HTTPException) -> TokenData:
    """
    Decodes the JWT token and extracts the username.
    Raises the provided HTTP exception if decoding fails or username is missing.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise http_exception
        return TokenData(username=username)
    except InvalidTokenError:
        raise http_exception


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """"
    Retrieves the current user based on the provided token.
    Raises HTTP 401 if the token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = get_token_data(token, credentials_exception)
    response = await get_user(username=token_data.username, collection=get_collection_user())
    if response is None:
        raise credentials_exception
    return User(**response)


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Ensures the current user is active (not disabled).
    Raises HTTP 400 if the user is inactive.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.get("/users/me", response_model=User)
def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)])-> User:
    """
    Retrieves the current authenticated user's information.
    Requires authentication via token.
    """
    return current_user


@router.post("/users", status_code=HTTP_201_CREATED)
async def create_user(user: NewUserInDB, token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """
    Creates a new user with hashed password.
    Requires authentication via token.
    """
    new_user = UserInDB(hashed_password=get_password_hash(user.password), **user.model_dump())
    await  get_collection_user().insert_one(new_user.model_dump())
    return User(**new_user.model_dump())

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
