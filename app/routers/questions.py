from fastapi import APIRouter, HTTPException, Depends, status
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/questions", tags=["questions"])

VALID_SUBJECTS = {
    "matematicas", "lenguajes", "conocimientoMedio", "formacionCivicaEtica",
    "ingles", "inglesExamen", "inglesExamen2doTrimestre", "lenguajes2doTrimestre",
    "matematicas2doTrimestre", "conocimientoMedio2doTrimestre",
    "formacionCivicaEtica2doTrimestre",
}


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.get("/{subject}")
async def get_questions(subject: str, _user=Depends(get_current_user)):
    if subject not in VALID_SUBJECTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    db = get_db()
    cursor = db["questions"].find({"subject": subject, "active": True})
    questions = [_serialize(doc) async for doc in cursor]
    return {"data": questions}
