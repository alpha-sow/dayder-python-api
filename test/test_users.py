from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.data import UserInDB, User, TokenData
from app.main import app
from app.routers import users

client = TestClient(app)

user = {
    "_id": "id",
    "username": "name",
    "email": "email",
    "full_name": "full_name",
    "disabled": False,
    "hashed_password": "fake-hashed-password"
}

user_in_db = UserInDB(
    id="id",
    username="name",
    email="email",
    full_name="full_name",
    disabled=False,
    hashed_password="fake-hashed-password",
)

collection = Mock()
collection.find_one = AsyncMock(return_value=user)

collection_failed = Mock()
collection_failed.find_one = AsyncMock(return_value=None)


@patch("app.routers.users.get_collection_user", return_value=collection)
def test_login(mock_collection):
    users.create_access_token = Mock(return_value="fake-token")
    users.authenticate_user = AsyncMock(return_value=UserInDB(
        id="id",
        username="name",
        email="email",
        full_name="full_name",
        disabled=False,
        hashed_password="fake-hashed-password",
    ))
    response = client.post("/token", data={"username": "name", "password": "password"})
    assert response.status_code == 200
    assert response.json() == {
        "access_token": "fake-token",
        "token_type": "bearer"
    }


@patch("app.routers.users.get_collection_user", return_value=collection_failed)
def test_login_failure(mock_collection):
    users.create_access_token = Mock(return_value="fake-token")
    users.authenticate_user = AsyncMock(return_value=None)
    response = client.post("/token", data={"username": "name", "password": "password"})
    assert response.status_code == 401

@patch("app.routers.users.get_collection_user", return_value=collection)
@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
def test_read_user_me(mock_auth, mock_collection):
    mock_user = User(
        username="name",
        email="email",
        full_name="full_name",
        disabled=False,
    )
    users.get_token_data = Mock(return_value=TokenData(username="fake-token"))
    response = client.get("/users/me", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    assert response.json() == mock_user.model_dump()

@patch("app.routers.users.get_collection_user", return_value=collection_failed)
@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
def test_read_user_me_failure(mock_auth, mock_collection):
    users.get_token_data = Mock(return_value=TokenData(username="fake-token"))
    response = client.get("/users/me", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 401
