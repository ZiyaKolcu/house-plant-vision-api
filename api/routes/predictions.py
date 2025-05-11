from fastapi import APIRouter, Depends
from api.db.database import Database
from api.core.security import get_current_user

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/my")
async def get_user_predictions(current_user: int = Depends(get_current_user)):
    query = """
        SELECT p.*
        FROM predictions p
        JOIN photo_submissions ps ON ps.id = p.submission_id
        WHERE ps.user_id = %s
        ORDER BY p.predicted_at DESC
    """
    rows = await Database.fetch_all(query, current_user)

    return rows
