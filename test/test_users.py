from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient

from app.data import UserInDB, User, TokenData
from app.main import app
from app.repositories import UserRepository
from app.routers import users

client = TestClient(app)


def test_login():
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


def test_login_failure():
    users.authenticate_user = AsyncMock(return_value=None)
    response = client.post("/token", data={"username": "name", "password": "password"})
    assert response.status_code == 401


def test_read_user_me():
    mock_user = User(
        username="name",
        email="email",
        full_name="full_name",
        disabled=False,
    )
    users.get_token_data = Mock(return_value=TokenData(username="fake-token"))
    UserRepository.get_user_by_username = AsyncMock(return_value={
        "_id": "id",
        "username": "name",
        "email": "email",
        "full_name": "full_name",
        "disabled": False,
    })
    with patch("app.dependencies.oauth2_scheme", return_value="fake-token"):
        response = client.get("/users/me", headers={"Authorization": "Bearer fake-token"})
        assert response.status_code == 200
        assert response.json() == mock_user.model_dump()


def test_read_user_me_failure():
    users.get_token_data = Mock(return_value=TokenData(username="fake-token"))
    UserRepository.get_user_by_username = AsyncMock(return_value=None)
    with patch("app.dependencies.oauth2_scheme", return_value="fake-token"):
        response = client.get("/users/me", headers={"Authorization": "Bearer fake-token"})
        assert response.status_code == 401
