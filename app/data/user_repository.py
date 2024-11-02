from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    email: str | None = None
    full_name: str | None = None
    hashed_password: str
    disabled: bool | None = None

