from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, Collection
from datetime import datetime, timedelta
from app.settings import settings
from app.dependencies import database, oauth2_scheme
from app.data import User, UserInDB, TokenData, Token
from passlib.context import CryptContext
import jwt
from jwt import InvalidTokenError
from starlette.status import HTTP_401_UNAUTHORIZED

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

@router.get("/me", response_model=User)
def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)])-> User:
    """
    Retrieves the current authenticated user's information.
    Requires authentication via token.
    """
    return current_user