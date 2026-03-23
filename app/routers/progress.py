from datetime import datetime
from fastapi import APIRouter, Depends, status
from app.models.progress import ProgressUpdate, ProgressPublic
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/{subject}", response_model=ProgressPublic)
async def get_progress(subject: str, user=Depends(get_current_user)):
    db = get_db()
    doc = await db["progress"].find_one({"user_id": str(user["_id"]), "subject": subject})
    if not doc:
        return ProgressPublic(
            subject=subject,
            answered_ids=[],
            incorrect_ids=[],
            updated_at=datetime.utcnow(),
        )
    return ProgressPublic(
        subject=doc["subject"],
        answered_ids=doc.get("answered_ids", []),
        incorrect_ids=doc.get("incorrect_ids", []),
        updated_at=doc["updated_at"],
    )


@router.put("/{subject}", response_model=ProgressPublic)
async def update_progress(subject: str, payload: ProgressUpdate, user=Depends(get_current_user)):
    db = get_db()
    now = datetime.utcnow()
    await db["progress"].update_one(
        {"user_id": str(user["_id"]), "subject": subject},
        {
            "$set": {
                "answered_ids": payload.answered_ids,
                "incorrect_ids": payload.incorrect_ids,
                "updated_at": now,
            }
        },
        upsert=True,
    )
    return ProgressPublic(
        subject=subject,
        answered_ids=payload.answered_ids,
        incorrect_ids=payload.incorrect_ids,
        updated_at=now,
    )
