from fastapi import APIRouter, HTTPException, Header, status
from app.models.user import UserCreate, TokenResponse
from app.database import get_db
from app.security import hash_password, verify_password, create_access_token
from app.config import settings
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, x_secret_key: str = Header(...)):
    if x_secret_key != settings.register_secret_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    db = get_db()
    existing = await db["users"].find_one({"username": payload.username})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    doc = {
        "username": payload.username,
        "hashed_password": hash_password(payload.password),
        "created_at": datetime.utcnow(),
    }
    result = await db["users"].insert_one(doc)
    return {"id": str(result.inserted_id), "username": payload.username}


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserCreate):
    db = get_db()
    user = await db["users"].find_one({"username": payload.username})
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(str(user["_id"]))
    return {"access_token": token}
