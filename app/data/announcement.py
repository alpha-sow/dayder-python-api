from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class Announcement(BaseModel):
    id:  str | None = None
    title: str = Field(...)
    description: str = Field(...)
    thumbnail: str | None = None
    createdAt: Optional[datetime] = Field(default_factory=datetime.now)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.now)