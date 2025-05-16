import os
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from fastapi.responses import FileResponse
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


@router.get("/image/{submission_id}")
async def get_submission_image(
    submission_id: int,
    current_user: int = Depends(get_current_user),
):
    query = """
        SELECT user_id, image_url
        FROM photo_submissions
        WHERE id = %s
    """
    row = await Database.fetchrow(query, submission_id)
    if not row:
        raise HTTPException(status_code=404, detail="Submission not found")

    if row["user_id"] != current_user:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this image"
        )

    image_path = row["image_url"]
    if not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Image file not found on server")

    return FileResponse(
        path=image_path,
        media_type="image/jpeg",  
        filename=os.path.basename(image_path),
    )
