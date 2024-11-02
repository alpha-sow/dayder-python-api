from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_401_UNAUTHORIZED

from app.data import User
from app.data.user_repository import UserRepository
from app.oauth2_scheme import oauth2_scheme

router = APIRouter(
    tags=["Users"],
)


def fake_hash_password(password: str):
    return "fakehashed" + password


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    response = await UserRepository.get_user_by_username(form_data.username)
    if response is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = User(id=str(response["_id"]), **response)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}


async def get_user(username: str):
    return await  UserRepository.get_user_by_username(username)


async def fake_decode_token(token):
    user = await get_user(token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = await fake_decode_token(token)
    if  user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(id=str(user["_id"]), **user)


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.get("/users/me", response_model=User)
def get_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
