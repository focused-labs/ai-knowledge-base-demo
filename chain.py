from operator import itemgetter

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import format_document
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

import config

llm = ChatOpenAI(temperature=0, model=config.CHAT_MODEL)
condense_question_prompt = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(condense_question_prompt)

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

SYSTEM_PROMPT = """Have a conversation with a human. Answer the question from the perspective of a {role}.
If you don't know the answer don't make one up, just say "Hmm, I'm not sure please contact 
work@focusedlabs.io for further assistance."  """
answer_prompt_base = """Answer the question based on the following context:
{context}

Question: {question}
"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(SYSTEM_PROMPT + answer_prompt_base)

store = {}


def combine_documents(docs, document_prompt):
    return "\n\n".join([format_document(doc, document_prompt) for doc in docs])


def get_session_history(session_id: str) -> ConversationBufferMemory:
    if session_id not in store:
        store[session_id] = ConversationBufferMemory(
            return_messages=True, output_key="answer", input_key="question"
        )
    return store[session_id]


def _get_loaded_memory(x):
    return get_session_history(x["session_id"]).load_memory_variables({"question": x["question"]})


def get_role(x):
    return x["role"]


def load_memory_chain():
    return RunnablePassthrough.assign(
        chat_history=RunnableLambda(_get_loaded_memory) | itemgetter("history"),
        role=RunnableLambda(get_role)
    )


def create_question_chain():
    return {
        "standalone_question": {
                                   "question": itemgetter("question"),
                                   "chat_history": lambda x: get_buffer_string(x["chat_history"]),
                               }
                               | CONDENSE_QUESTION_PROMPT
                               | llm
                               | StrOutputParser(),
        "role": itemgetter("role")
    }


def retrieve_documents_chain(vector_store):
    retriever = vector_store.as_retriever()
    return {
        "role": itemgetter("role"),
        "docs": itemgetter("standalone_question") | retriever,
        "question": lambda x: x["standalone_question"],
    }


def create_answer_chain():
    final_inputs = {
        "role": itemgetter("role"),
        "context": lambda x: combine_documents(x["docs"], DEFAULT_DOCUMENT_PROMPT),
        "question": itemgetter("question")
    }
    return {
        "answer": final_inputs | ANSWER_PROMPT | llm,
        "docs": itemgetter("docs")
    }


class Chain:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.loaded_memory = load_memory_chain()
        self.standalone_question = create_question_chain()

        self.retrieved_documents = retrieve_documents_chain(self.vector_store)
        self.answer = create_answer_chain()

        self.complete_chain = self.loaded_memory | self.standalone_question | self.retrieved_documents | self.answer

    def save_memory(self, question: str, answer: str, session_id: str):
        get_session_history(session_id).save_context({"question": question}, {"answer": answer})
