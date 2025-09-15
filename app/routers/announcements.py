from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.motor import paginate as motor_paginate
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.data import Announcement
from app.dependencies import database, oauth2_scheme

router = APIRouter()


def get_collection_announcement():
    return database.announcement


@router.get("", response_model=Page[Announcement])
async def read_announcements(token: Annotated[str, Depends(oauth2_scheme)])-> Page[Announcement]:
    return await motor_paginate(get_collection_announcement())


@router.get("/{id}")
async def read_announcement(
        id: str,
        token: Annotated[str, Depends(oauth2_scheme)],
) -> Announcement:
    announcement = await get_collection_announcement().find_one(ObjectId(id))
    if announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return Announcement(**announcement)


@router.post("", status_code=HTTP_201_CREATED)
async def create_announcement(
        announcement: Announcement,
        token: Annotated[str, Depends(oauth2_scheme)],
):
    await get_collection_announcement().insert_one(announcement.model_dump(exclude={'id'}))


@router.delete("/{announcement_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_announcement(
        announcement_id: str,
        token: Annotated[str, Depends(oauth2_scheme)],
):
    await get_collection_announcement().delete_one(ObjectId(announcement_id))


@router.put("")
async def update_announcement(
        announcement: Announcement,
        token: Annotated[str, Depends(oauth2_scheme)],
):
    await get_collection_announcement().put_one(announcement)
