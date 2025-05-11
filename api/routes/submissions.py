from fastapi import APIRouter, File, UploadFile, Depends
from api.core.security import get_current_user
from api.services.submission_service import handle_submission
from api.db.database import Database

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/", status_code=201)
async def submit_photo(
    file: UploadFile = File(...),
    current_user: int = Depends(get_current_user),
):
    return await handle_submission(file, current_user)


@router.get("/my")
async def get_user_submissions(current_user: int = Depends(get_current_user)):
    query = """
        SELECT id, image_url, submitted_at, status
        FROM photo_submissions
        WHERE user_id = %s
        ORDER BY submitted_at DESC
    """
    rows = await Database.fetch_all(query, current_user)

    return rows
