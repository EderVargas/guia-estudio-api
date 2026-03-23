# AGENTS.md

## Project purpose

REST API backend for the guia-estudio interactive quiz platform. Built with FastAPI, Motor (async MongoDB driver), and JWT authentication. Deployed to Render.com, connected to MongoDB Atlas M0.

**Frontend**: https://edervargas.github.io/guia-estudio/  
**Repo**: guia-estudio-api (separate from frontend repo by design)

---

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.115 |
| Async DB driver | Motor 3.5 (MongoDB Atlas) |
| Auth | JWT via python-jose + passlib/bcrypt |
| Settings | pydantic-settings (.env file) |
| Deploy | Render.com (Web Service, free tier) |
| DB | MongoDB Atlas M0 |

---

## Project structure

```
app/
  main.py          # FastAPI app, CORS, lifespan, router registration
  config.py        # Settings loaded from environment via pydantic-settings
  database.py      # Motor client singleton, get_db() helper
  security.py      # Password hashing, JWT creation/validation, get_current_user dependency
  models/
    user.py        # UserCreate, UserInDB, UserPublic, TokenResponse
    question.py    # Question, QuestionPublic, AnswerOption
    progress.py    # Progress, ProgressUpdate, ProgressPublic
  routers/
    auth.py        # POST /auth/register (secret-key protected), POST /auth/login
    questions.py   # GET /questions/{subject} (JWT required)
    progress.py    # GET/PUT /progress/{subject} (JWT required)
    stats.py       # GET /stats (JWT required)
scripts/
  migrate_questions.py  # One-time migration: JSON files -> MongoDB questions collection
render.yaml        # Render.com deployment config
requirements.txt
.env.example
```

---

## Environment variables

All variables are defined in `.env` (local, gitignored) and `.env.example` (committed).

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | Full Atlas connection string |
| `DB_NAME` | Database name (default: `guia-estudio`) |
| `JWT_SECRET` | Secret for signing JWT tokens |
| `JWT_ALGORITHM` | HS256 |
| `JWT_EXPIRE_MINUTES` | Token TTL in minutes (default: 1440) |
| `REGISTER_SECRET_KEY` | Header secret for POST /auth/register (Postman/PS1 only) |
| `FRONTEND_ORIGIN` | Allowed CORS origin |

---

## API endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | none | Liveness check |
| POST | `/auth/register` | `X-Secret-Key` header | Create user (admin only via Postman/PS1) |
| POST | `/auth/login` | none | Returns JWT |
| GET | `/questions/{subject}` | JWT Bearer | All active questions for a subject |
| GET | `/progress/{subject}` | JWT Bearer | User progress for a subject |
| PUT | `/progress/{subject}` | JWT Bearer | Save/update user progress |
| GET | `/stats` | JWT Bearer | Aggregated stats across all subjects |

---

## MongoDB collections

### users
```json
{
  "_id": ObjectId,
  "username": "string",
  "hashed_password": "bcrypt hash",
  "created_at": ISODate
}
```

### questions
```json
{
  "_id": ObjectId,
  "subject": "matematicas",
  "category": "Conteo de Elementos",
  "type": "multiple-choice",
  "question": "string",
  "answers": [{ "option": "string", "correct": true }],
  "correctAnswer": null,
  "audioText": null,
  "image": "assets/images/matematicas/1.jpg",
  "active": true
}
```

### progress
```json
{
  "_id": ObjectId,
  "user_id": "string (ObjectId as str)",
  "subject": "matematicas",
  "answered_ids": ["mongo_id_1", "..."],
  "incorrect_ids": ["mongo_id_2", "..."],
  "updated_at": ISODate
}
```

---

## Local development setup

```bash
cd guia-estudio-api
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env            # Fill in real values
uvicorn app.main:app --reload
```

API docs available at: http://localhost:8000/docs

---

## Data migration

Run once after setting up MongoDB Atlas:

```bash
python scripts/migrate_questions.py --json-dir ../guia-estudio-front/docs/assets
```

This deletes and reinserts all questions per subject. Safe to re-run when JSON source files are updated.

---

## Registering a user

Only via `POST /auth/register` with the `X-Secret-Key` header:

```powershell
Invoke-RestMethod -Uri "https://<api>.onrender.com/auth/register" `
  -Method POST `
  -Headers @{ "X-Secret-Key" = "your_register_secret"; "Content-Type" = "application/json" } `
  -Body '{"username": "student1", "password": "securepass"}'
```

---

## Conventions

- No emojis in code, logs, comments, or commits.
- Responses use snake_case for JSON keys.
- All DB access is async (Motor).
- No admin UI. Question management is done directly in MongoDB Atlas or by re-running the migration script.
- Subject keys must match the `VALID_SUBJECTS` set in `routers/questions.py` and the `SUBJECTS` object in the frontend's `script.js`.
