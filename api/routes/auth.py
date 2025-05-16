from fastapi import APIRouter, Depends, HTTPException, status, Request
from api.db.database import Database
from api.schemas.auth import UserProfile, UserCreate, UserLogin, Token
from api.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from api.core.blacklist import blacklist_token
from api.core.config import settings

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
async def login(user: UserLogin):
    query = "SELECT id, password FROM users WHERE email = %s"
    row = await Database.fetchrow(query, user.email)
    if not row or not verify_password(user.password, row["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": str(row["id"])})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signout")
async def signout(request: Request, current_user: int = Depends(get_current_user)):
    token = request.headers.get("authorization").split(" ")[1]
    await blacklist_token(token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return {"msg": "Successfully signed out"}


@router.get("/me", response_model=UserProfile)
async def read_profile(current_user: int = Depends(get_current_user)):
    query = """
        SELECT id, username, email, created_at, updated_at
        FROM users
        WHERE id = %s
    """
    row = await Database.fetchrow(query, current_user)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return row
