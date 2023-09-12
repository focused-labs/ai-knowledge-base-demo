from sqlalchemy import Column, Integer, String, UUID

from database import Base


class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(UUID, unique=True, index=True)
    created_at = Column(String)
    question = Column(String)
    response = Column(String)
    error_message = Column(String)
