from typing import Optional, List
from pydantic import BaseModel, Field


class AnswerOption(BaseModel):
    option: str
    correct: Optional[bool] = None


class Question(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    subject: str
    category: str
    type: str = "multiple-choice"
    question: str
    answers: Optional[List[AnswerOption]] = None
    correct_answer: Optional[str] = Field(default=None, alias="correctAnswer")
    audio_text: Optional[str] = Field(default=None, alias="audioText")
    image: Optional[str] = None
    active: bool = True

    class Config:
        populate_by_name = True


class QuestionPublic(BaseModel):
    id: str
    subject: str
    category: str
    type: str
    question: str
    answers: Optional[List[AnswerOption]] = None
    correct_answer: Optional[str] = None
    audio_text: Optional[str] = None
    image: Optional[str] = None
