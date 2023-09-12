from datetime import datetime
import json
from uuid import uuid4
import conversation_repository
from agent import Agent
from database import get_db
from models.conversation import Conversation
from models.question import Question
from models.session import Session


class QueryService:

    def __init__(self):
        self.agents = {}

    def _create_query_session(self, personality):
        session_id = uuid4()
        self.agents[session_id] = Agent(personality=personality)
        return session_id

    def query(self, question: Question):
        session_id = question.session_id
        if session_id not in self.agents:
            session_id = self._create_query_session(personality=question.role)
        try:
            agent = self.agents[session_id]
            answer = agent.query_agent(user_input=question.text)
            response_formatted = json.loads(answer, strict=False)
            conversation_repository.create_conversation(
                db=next(get_db()),
                conversation=Conversation(session_id=session_id, question=question.text, created_at=datetime.now(),
                                          response=response_formatted['result']))
            return {"response": response_formatted, "session_id": session_id}
        except Exception as e:
            conversation_repository.create_conversation(
                db=next(get_db()),
                conversation=Conversation(session_id=session_id, question=question.text, created_at=datetime.now(),
                                          response="", error_message=str(e)))
            raise e

    def delete_query_session(self, session: Session):
        if session.session_id in self.agents:
            self.agents.pop(session.session_id)
