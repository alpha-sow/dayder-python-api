from typing import Optional
from pydantic import BaseModel, Field
from app.data.py_object_id import py_object_id


class User(BaseModel):
    id: Optional[py_object_id] = Field(alias="_id", default=None)
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = False