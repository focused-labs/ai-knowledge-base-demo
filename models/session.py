from uuid import UUID

from pydantic import BaseModel


class Session(BaseModel):
    session_id: UUID