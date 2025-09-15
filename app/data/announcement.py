from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.data.py_object_id import py_object_id


class Announcement(BaseModel):
    id: Optional[py_object_id] = Field(alias="_id", default=None)
    title: str = Field(...)
    description: str = Field(...)
    thumbnail: str | None = None
    createdAt: Optional[datetime] = Field(default_factory=datetime.now)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.now)
