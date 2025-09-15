from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from bson import ObjectId

from app.data import UserInDB, User, NewUserInDB
from app.main import app
from app.routers import users

client = TestClient(app)

user = {
    "_id": ObjectId("507f1f77bcf86cd799439011"),
    "username": "name",
    "email": "email",
    "full_name": "full_name",
    "disabled": False,
    "hashed_password": "fake-hashed-password"
}

user_in_db = UserInDB(
    id="507f1f77bcf86cd799439011",
    username="name",
    email="email",
    full_name="full_name",
    disabled=False,
    hashed_password="fake-hashed-password",
)

collection = Mock()
collection.find_one = AsyncMock(return_value=user)
collection.insert_one = AsyncMock()

collection_failed = Mock()
collection_failed.find_one = AsyncMock(return_value=None)


@patch("app.routers.users.get_collection_user", return_value=collection)
@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
@patch("app.routers.users.motor_paginate")
def test_read_users(mock_paginate, mock_auth, mock_collection):
    from fastapi_pagination import Page
    mock_paginate.return_value = Page(
        items=[],
        total=0,
        page=1,
        size=50,
        pages=0
    )
    response = client.get("/users", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200


@patch("app.routers.users.get_collection_user", return_value=collection)
@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
def test_create_user(mock_auth, mock_collection):
    new_user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "password123",
        "disabled": False
    }
    response = client.post("/users", json=new_user_data, headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 201
    assert "username" in response.json()
    assert response.json()["username"] == "newuser"


@patch("app.routers.users.get_collection_user", return_value=collection)
@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
def test_read_user_by_id(mock_auth, mock_collection):
    response = client.get("/users/507f1f77bcf86cd799439011", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    assert response.json()["username"] == "name"


@patch("app.routers.users.get_collection_user", return_value=collection_failed)
@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
def test_read_user_by_id_not_found(mock_auth, mock_collection):
    response = client.get("/users/507f1f77bcf86cd799439011", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 404
