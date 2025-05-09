from fastapi import APIRouter, File, UploadFile, Depends
from api.core.security import get_current_user
from api.services.submission_service import handle_submission

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/", status_code=201)
async def submit_photo(
    file: UploadFile = File(...),
    current_user: int = Depends(get_current_user),
):
    return await handle_submission(file, current_user)
