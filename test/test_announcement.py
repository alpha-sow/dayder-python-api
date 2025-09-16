from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

client.headers = {"Authorization": "Bearer fake-token"}

mongo_response = {
    "_id": "6720b1dcfded4d38b1c9b560",
    "title": "title",
    "description": "description",
    "thumbnail": "thumbnail",
    "createdAt": "2024-10-29T09:58:52.102000",
    "updatedAt": "2024-10-29T09:58:52.102000"
}

pagination = {
    "items": [mongo_response],
    "page": 1,
    "pages": 1,
    "size": 50,
    "total": 3
}

collection = Mock()
collection.find_one = AsyncMock(return_value=mongo_response)
collection.insert_one = AsyncMock()
collection.delete_one = AsyncMock()

collection_failed = Mock()
collection_failed.find_one = AsyncMock(return_value=None)


@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
@patch("app.routers.announcements.motor_paginate", return_value=pagination)
def test_read_announcements(mock_motor_paginate, mock_auth):
    response = client.get("/api/announcements")
    assert response.status_code == 200
    assert response.json() == pagination


@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
@patch("app.routers.announcements.get_collection_announcement", return_value=collection)
def test_read_announcement_by_id(mock_collection, mock_auth):
    response = client.get("/api/announcements/6725225a2dc0df1bda38d279")
    assert response.status_code == 200
    assert response.json() == mongo_response


@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
@patch("app.routers.announcements.get_collection_announcement", return_value=collection_failed)
def test_read_announcement_by_id_failed(mock_collection, mock_auth):
    response = client.get("/api/announcements/6725225a2dc0df1bda38d279")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Announcement not found'}


@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
@patch("app.routers.announcements.get_collection_announcement", return_value=collection)
def test_create_announcement(mock_collection, mock_auth):
    response = client.post("/api/announcements", json={
        "title": "string",
        "description": "string",
        "thumbnail": "string",
    })
    assert response.status_code == 201


@patch("app.dependencies.oauth2_scheme", return_value="fake-token")
@patch("app.routers.announcements.get_collection_announcement", return_value=collection)
def test_delete_announcement(mock_collection, mock_auth):
    response = client.delete("/api/announcements/6725225a2dc0df1bda38d279")
    assert response.status_code == 204
