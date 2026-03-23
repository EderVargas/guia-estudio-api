"""
Migration script: loads all subject JSON files into MongoDB.

Usage:
    python scripts/migrate_questions.py --json-dir ../guia-estudio-front/docs/assets

Each document inserted:
{
    subject:       str,
    category:      str,
    type:          str,
    question:      str,
    answers:       list | None,
    correctAnswer: str | None,
    audioText:     str | None,
    image:         str | None,
    active:        bool,
}
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add project root to sys.path so 'app' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

SUBJECT_FILES = {
    "matematicas":                    "matematicas.json",
    "lenguajes":                      "lenguajes.json",
    "conocimientoMedio":              "conocimientoMedio.json",
    "formacionCivicaEtica":           "formacionCivicaEtica.json",
    "ingles":                         "inglesDictationAll.json",
    "inglesExamen":                   "inglesExamen.json",
    "inglesExamen2doTrimestre":       "inglesExamen2doTrimestre.json",
    "lenguajes2doTrimestre":          "lenguajes2doTrimestre.json",
    "matematicas2doTrimestre":        "matematicas2doTrimestre.json",
    "conocimientoMedio2doTrimestre":  "conocimientoMedio2doTrimestre.json",
    "formacionCivicaEtica2doTrimestre": "formacionCivicaEtica2doTrimestre.json",
}


def _build_doc(subject: str, raw: dict) -> dict:
    return {
        "subject":       subject,
        "category":      raw.get("category", ""),
        "type":          raw.get("type", "multiple-choice"),
        "question":      raw.get("question", ""),
        "answers":       raw.get("answers"),
        "correctAnswer": raw.get("correctAnswer"),
        "audioText":     raw.get("audioText"),
        "image":         raw.get("image"),
        "active":        True,
    }


async def migrate(json_dir: Path):
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.db_name]
    collection = db["questions"]

    total_inserted = 0

    for subject, filename in SUBJECT_FILES.items():
        filepath = json_dir / filename
        if not filepath.exists():
            print(f"[SKIP] {subject}: file not found at {filepath}")
            continue

        with filepath.open(encoding="utf-8") as f:
            data = json.load(f)

        # Support flat { "data": [...] } and categorized { "categories": [{ "data": [...] }] }
        if "categories" in data:
            raw_questions = [q for cat in data["categories"] for q in cat.get("data", [])]
        else:
            raw_questions = data.get("data", [])

        if not raw_questions:
            print(f"[SKIP] {subject}: empty data array")
            continue

        docs = [_build_doc(subject, q) for q in raw_questions]

        # Remove existing documents for this subject before reinserting
        delete_result = await collection.delete_many({"subject": subject})
        result = await collection.insert_many(docs)

        print(
            f"[OK] {subject}: removed {delete_result.deleted_count}, "
            f"inserted {len(result.inserted_ids)}"
        )
        total_inserted += len(result.inserted_ids)

    # Ensure index on subject for query performance
    await collection.create_index("subject")
    await collection.create_index([("subject", 1), ("active", 1)])

    print(f"\nDone. Total questions inserted: {total_inserted}")
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-dir",
        required=True,
        help="Path to the folder containing the subject JSON files",
    )
    args = parser.parse_args()
    json_dir = Path(args.json_dir).resolve()

    if not json_dir.is_dir():
        print(f"Error: {json_dir} is not a valid directory")
        sys.exit(1)

    asyncio.run(migrate(json_dir))
