from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Question(BaseModel):
    text: str
    role: str
    session_id: Optional[UUID]