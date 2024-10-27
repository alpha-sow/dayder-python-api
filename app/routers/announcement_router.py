from typing import List

from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.data import AnnouncementRepository, Announcement

router = APIRouter(
    prefix="/announcements",
    tags=['Announcement'],
)

@router.get("/")
async def get_all_announcements() -> List[Announcement]:
    result = []
    response = await AnnouncementRepository.find_all()
    for announcement in response:
        result.append(Announcement(id= str(announcement["_id"]) ,**announcement))
    return result

@router.get("/{announcement_id}")
async def get_announcement_by_id(announcement_id: str) -> Announcement:
    announcement = await AnnouncementRepository.find_one(announcement_id)
    if announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return Announcement(id= str(announcement["_id"]) ,**announcement)

@router.post("/", status_code=HTTP_201_CREATED)
async def create_announcement(announcement: Announcement):
    await AnnouncementRepository.insert_one(announcement)

@router.delete("/{announcement_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_announcement(announcement_id: str):
    await AnnouncementRepository.delete_one(announcement_id)
