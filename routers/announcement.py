from fastapi import APIRouter

router = APIRouter()

@router.get("/announcement")
def get_all_announcement():
    return []