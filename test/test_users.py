from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from bson import ObjectId

from app.data import UserInDB, User, NewUserInDB
from app.data.user_role import UserRole
from app.main import app
from app.routers.authentication import get_current_active_user
from app.dependencies import oauth2_scheme

user = {
    "_id": ObjectId("507f1f77bcf86cd799439011"),
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "disabled": False,
    "hashed_password": "fake-hashed-password",
    "role": UserRole.ADMIN
}

user_in_db = UserInDB(
    id="507f1f77bcf86cd799439011",
    username="testuser",
    email="test@example.com",
    full_name="Test User",
    disabled=False,
    hashed_password="fake-hashed-password",
    role=UserRole.ADMIN
)

collection = Mock()
collection.find_one = AsyncMock(return_value=user)
collection.insert_one = AsyncMock()

collection_failed = Mock()
collection_failed.find_one = AsyncMock(return_value=None)

# Mock authentication dependencies
def mock_oauth2_scheme():
    return "fake-token"

def mock_current_user():
    return user_in_db

# Override dependencies in the app
app.dependency_overrides[oauth2_scheme] = mock_oauth2_scheme
app.dependency_overrides[get_current_active_user] = mock_current_user

client = TestClient(app)


@patch("app.routers.users.get_collection_user", return_value=collection)
@patch("app.routers.users.motor_paginate")
def test_read_users(mock_paginate, mock_collection):
    from fastapi_pagination import Page
    mock_paginate.return_value = Page(
        items=[],
        total=0,
        page=1,
        size=50,
        pages=0
    )
    response = client.get("/api/users", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200


@patch("app.routers.users.get_collection_user", return_value=collection)
def test_create_user(mock_collection):
    new_user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "password123",
        "disabled": False
    }
    response = client.post("/api/users", json=new_user_data, headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 201
    assert "username" in response.json()
    assert response.json()["username"] == "newuser"


@patch("app.routers.users.get_collection_user", return_value=collection)
def test_read_user_by_id(mock_collection):
    response = client.get("/api/users/507f1f77bcf86cd799439011", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


@patch("app.routers.users.get_collection_user", return_value=collection_failed)
def test_read_user_by_id_not_found(mock_collection):
    response = client.get("/api/users/507f1f77bcf86cd799439011", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 404
