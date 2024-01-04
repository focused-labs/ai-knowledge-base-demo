from pydantic import BaseModel


class Question(BaseModel):
    text: str
    role: str
    session_id: str
