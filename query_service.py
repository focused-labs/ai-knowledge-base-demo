from datetime import datetime
from uuid import uuid4

import conversation_repository
from chain import Chain
from database import get_db
from models.conversation import Conversation
from models.question import Question
from models.session import Session
from pinecone_manager import PineconeManager


class QueryService:

    def __init__(self):
        self.vectorstore_manager = PineconeManager()
        self.chain = Chain(vector_store=self.vectorstore_manager.vectorstore)

    def query(self, question: Question):
        if not question.session_id:
            question.session_id = str(uuid4())
        try:
            result = self.chain.complete_chain.invoke(
                {"question": question.text, "session_id": question.session_id, "role": question.role})
            answer = result["answer"].content
            self.chain.save_memory(question.text, answer, str(question.session_id))

            print("Chat History: \n", result["chat_history"], "\n\n")
            print("Standalone Question: \n", result["standalone_question"], "\n\n")

            sources = []
            for doc in result["docs"]:
                source_url = doc.metadata['URL']
                sources.append({"URL": source_url})

            response_formatted = {"result": answer, "sources": sources}

            conversation_repository.create_conversation(
                db=next(get_db()),
                conversation=Conversation(session_id=question.session_id, question=question.text,
                                          created_at=datetime.now(),
                                          response=response_formatted['result']))
        except Exception as e:
            conversation_repository.create_conversation(
                db=next(get_db()),
                conversation=Conversation(session_id=question.session_id, question=question.text,
                                          created_at=datetime.now(),
                                          response="", error_message=str(e)))
            print(f"Failed to execute query or log response. Error: {e}")
            raise e

        return {"response": response_formatted, "session_id": question.session_id}

    def delete_query_session(self, session: Session):
        # TODO: Not yet implemented
        return
