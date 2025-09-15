from typing import List

from fastapi import HTTPException, status
from fastapi.params import Depends

from app.data.user import User
from app.data.user_role import UserRole
from app.routers.authentication import get_current_active_user


class RequireRole:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_active_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user