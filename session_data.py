from pydantic import BaseModel
from uuid import UUID


class SessionData(BaseModel):
    agent_name: UUID



