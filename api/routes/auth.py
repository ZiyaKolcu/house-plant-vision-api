from fastapi import APIRouter, Depends, HTTPException, status
from api.db.database import Database
from api.schemas.auth import UserCreate, Token
from api.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from api.core.blacklist import blacklist_token
from api.core.config import settings
from fastapi import Request

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=Token)
async def signup(user: UserCreate):
    hashed = get_password_hash(user.password)
    query = (
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id"
    )
    row = await Database.fetchrow(query, user.username, user.email, hashed)
    user_id = row["id"]
    access_token = create_access_token({"sub": str(user_id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login(form_data: UserCreate):
    query = "SELECT id, password FROM users WHERE username=%s OR email=%s"
    row = await Database.fetchrow(query, form_data.username, form_data.email)
    if not row or not verify_password(form_data.password, row["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": str(row["id"])})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signout")
async def signout(request: Request, current_user: int = Depends(get_current_user)):
    token = request.headers.get("authorization").split(" ")[1]
    await blacklist_token(token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return {"msg": "Successfully signed out"}
