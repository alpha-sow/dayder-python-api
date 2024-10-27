from unittest.mock import AsyncMock
from starlette.testclient import TestClient
from app.data import AnnouncementRepository
from app.main import app

client = TestClient(app)

mongo_response = {
    "_id": "6720b1dcfded4d38b1c9b560",
    "title": "string",
    "description": "string",
    "thumbnail": "string",
    "createdAt": "2024-10-29T09:58:52.102000",
    "updatedAt": "2024-10-29T09:58:52.102000"
}

announcement_response = {
    "id": "6720b1dcfded4d38b1c9b560",
    "title": "string",
    "description": "string",
    "thumbnail": "string",
    "createdAt": "2024-10-29T09:58:52.102000",
    "updatedAt": "2024-10-29T09:58:52.102000"
}


def test_get_all_announcements():
    AnnouncementRepository.find_all = AsyncMock(return_value=[mongo_response])
    response = client.get("/announcements")
    assert response.status_code == 200
    assert response.json() == [announcement_response]


def test_get_announcement_by_id():
    AnnouncementRepository.find_one = AsyncMock(return_value=mongo_response)
    response = client.get("/announcements/6725225a2dc0df1bda38d279")
    assert response.status_code == 200
    assert response.json() == announcement_response
    AnnouncementRepository.find_one = AsyncMock(return_value=None)
    response = client.get("/announcements/6725225a2dc0df1bda38d279")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Announcement not found'}


def test_create_announcement():
    AnnouncementRepository.insert_one = AsyncMock()
    response = client.post("/announcements", json={
        "title": "string",
        "description": "string",
        "thumbnail": "string",
    })
    assert response.status_code == 201


def test_delete_announcement():
    AnnouncementRepository.delete_one = AsyncMock()
    response = client.delete("/announcements/6725225a2dc0df1bda38d279")
    assert response.status_code == 204
