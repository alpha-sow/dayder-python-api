from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.data.py_object_id import py_object_id
from .user_role import UserRole


class User(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    id: Optional[py_object_id] = Field(alias="_id", default=None)
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = False
    role: UserRole | None = UserRole.USER