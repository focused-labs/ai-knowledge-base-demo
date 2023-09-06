import json
import os
from uuid import uuid4

from agent import Agent
from models.question import Question
from models.session import Session
from logger import save_question, save_error


class QueryService:

    def __init__(self):
        self.agents = {}

    def _create_query_session(self):
        session_id = uuid4()
        self.agents[session_id] = Agent()
        return session_id

    def query(self, question: Question):
        session_id = question.session_id
        if session_id not in self.agents:
            session_id = self._create_query_session()
        try:
            agent = self.agents[session_id]
            answer = agent.query_agent(user_input=question.text, personality=question.role)
            response_formatted = json.loads(answer)
            save_question(session_id, question.text, response_formatted)
            return {"response": response_formatted, "session_id": session_id}
        except Exception as e:
            error = save_error(session_id, question.text, str(e), os.getenv("GOOGLE_API_SPREADSHEET_ID"),
                               os.getenv("GOOGLE_API_RANGE_NAME"))
            raise e

    def delete_query_session(self, session: Session):
        if session.session_id in self.agents:
            self.agents.pop(session.session_id)
