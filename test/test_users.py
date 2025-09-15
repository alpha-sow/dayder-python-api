from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from bson import ObjectId

from app.data import UserInDB, User, NewUserInDB
from app.data.user_role import UserRole
from app.data.token import TokenData
from app.main import app
from app.routers import users, authentication

client = TestClient(app)

user = {
    "_id": ObjectId("507f1f77bcf86cd799439011"),
    "username": "name",
    "email": "email",
    "full_name": "full_name",
    "disabled": False,
    "hashed_password": "fake-hashed-password",
    "role": UserRole.ADMIN
}

user_in_db = UserInDB(
    id="507f1f77bcf86cd799439011",
    username="name",
    email="email",
    full_name="full_name",
    disabled=False,
    hashed_password="fake-hashed-password",
    role=UserRole.ADMIN
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
    response = client.get("/api/users", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200


@patch("app.routers.users.get_collection_user", return_value=collection)
@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
def test_create_user(mock_auth, mock_collection):
    # Mock get_token_data to return admin user token data
    authentication.get_token_data = Mock(return_value=TokenData(username="admin"))
    
    # Add admin user to the mocked collection
    admin_user = {
        "_id": ObjectId("507f1f77bcf86cd799439012"),
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "disabled": False,
        "hashed_password": "fake-hashed-password",
        "role": UserRole.ADMIN
    }
    
    # Mock find_one to return the admin user when username is "admin"
    async def mock_find_one(filter_dict):
        if filter_dict.get("username") == "admin":
            return admin_user
        return user
    
    collection.find_one = AsyncMock(side_effect=mock_find_one)
    
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
@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
def test_read_user_by_id(mock_auth, mock_collection):
    response = client.get("/api/users/507f1f77bcf86cd799439011", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    assert response.json()["username"] == "name"


@patch("app.routers.users.get_collection_user", return_value=collection_failed)
@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
def test_read_user_by_id_not_found(mock_auth, mock_collection):
    response = client.get("/api/users/507f1f77bcf86cd799439011", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 404
