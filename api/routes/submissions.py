import os
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from fastapi.responses import FileResponse
from api.core.security import get_current_user
from api.services.submission_service import handle_submission
from api.db.database import Database
from api.utils.logger import log_usage  # logger import edildi

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/", status_code=201)
async def submit_photo(
    file: UploadFile = File(...),
    current_user: int = Depends(get_current_user),
):
    try:
        result = await handle_submission(file, current_user)
        await log_usage(current_user, "submit_photo", "success")
        return result
    except Exception as e:
        await log_usage(current_user, "submit_photo", "failed", str(e))
        raise


@router.get("/my")
async def get_user_submissions(current_user: int = Depends(get_current_user)):
    try:
        query = """
            SELECT id, image_url, submitted_at, status
            FROM photo_submissions
            WHERE user_id = %s
            ORDER BY submitted_at DESC
        """
        rows = await Database.fetch_all(query, current_user)
        await log_usage(current_user, "get_user_submissions", "success")
        return rows
    except Exception as e:
        await log_usage(current_user, "get_user_submissions", "failed", str(e))
        raise


@router.get("/image/{submission_id}")
async def get_submission_image(
    submission_id: int,
    current_user: int = Depends(get_current_user),
):
    try:
        query = """
            SELECT user_id, image_url
            FROM photo_submissions
            WHERE id = %s
        """
        row = await Database.fetchrow(query, submission_id)
        if not row:
            await log_usage(
                current_user, "get_submission_image", "failed", "Submission not found"
            )
            raise HTTPException(status_code=404, detail="Submission not found")

        if row["user_id"] != current_user:
            await log_usage(
                current_user, "get_submission_image", "failed", "Unauthorized access"
            )
            raise HTTPException(
                status_code=403, detail="Not authorized to access this image"
            )

        image_path = row["image_url"]
        if not os.path.isfile(image_path):
            await log_usage(
                current_user, "get_submission_image", "failed", "Image file not found"
            )
            raise HTTPException(
                status_code=404, detail="Image file not found on server"
            )

        await log_usage(current_user, "get_submission_image", "success")
        return FileResponse(
            path=image_path,
            media_type="image/jpeg",
            filename=os.path.basename(image_path),
        )
    except Exception as e:
        await log_usage(current_user, "get_submission_image", "failed", str(e))
        raise


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_submission(
    submission_id: int,
    current_user: int = Depends(get_current_user),
):
    try:
        fetch_query = """
            SELECT user_id, image_url
            FROM photo_submissions
            WHERE id = %s
        """
        row = await Database.fetchrow(fetch_query, submission_id)
        if not row:
            await log_usage(
                current_user, "delete_submission", "failed", "Submission not found"
            )
            raise HTTPException(status_code=404, detail="Submission not found")

        if row["user_id"] != current_user:
            await log_usage(
                current_user,
                "delete_submission",
                "failed",
                "Unauthorized deletion attempt",
            )
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this submission"
            )

        image_path = row["image_url"]

        delete_query = "DELETE FROM photo_submissions WHERE id = %s"
        await Database.execute(delete_query, submission_id)

        try:
            if os.path.isfile(image_path):
                os.remove(image_path)
        except Exception as e:
            await log_usage(
                current_user,
                "delete_submission",
                "warning",
                f"Image deletion failed: {e}",
            )

        await log_usage(current_user, "delete_submission", "success")
    except Exception as e:
        await log_usage(current_user, "delete_submission", "failed", str(e))
        raise
