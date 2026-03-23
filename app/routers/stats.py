from fastapi import APIRouter, Depends
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
async def get_stats(user=Depends(get_current_user)):
    db = get_db()
    user_id = str(user["_id"])

    cursor = db["progress"].find({"user_id": user_id})
    subjects_progress = []

    async for doc in cursor:
        subject = doc["subject"]
        total_in_subject = await db["questions"].count_documents(
            {"subject": subject, "active": True}
        )
        subjects_progress.append({
            "subject": subject,
            "answered": len(doc.get("answered_ids", [])),
            "incorrect_pending": len(doc.get("incorrect_ids", [])),
            "total": total_in_subject,
        })

    return {"username": user["username"], "subjects": subjects_progress}
