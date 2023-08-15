import json
import logging
import sys
from contextlib import asynccontextmanager
from uuid import uuid4, UUID

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chat_engine import create_agent, query_agent
from persistence import save_question
from importer import import_notion_data, import_web_scrape_data

allowed_origins = [
    "http://localhost:3000",
    "https://fl-ai-knowledgehub-h27h6.ondigitalocean.app/",
    "https://chat.withfocus.com/",
    "https://chat.focusedlabs.io/"
]

agents = {}


def init_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


def load_notion_documents():
    print("Loading notion docs")
    # import_notion_data()


def load_web_scrape_documents():
    print("Loading web scraped docs")
    # import_web_scrape_data()


class Question(BaseModel):
    text: str
    role: str
    session_id: UUID | None


class Session(BaseModel):
    session_id: UUID


personalities = {
    "none": "website visitor",
    "candidate": "potential employee",
    "client": "potential client"
}


def define_personality(question: Question):
    if question.role is None:
        question.role = "none"
    personality = personalities[question.role]
    if personality is None:
        personality = personalities["none"]
    return personality


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logging()

    # Load documents. This can be slow so block the API until ready
    load_notion_documents()
    load_web_scrape_documents()

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/query/")
async def query(question: Question):
    session_id = question.session_id
    if session_id not in agents:
        session_id = create_session()
    personality = define_personality(question)
    response = json.loads(query_agent(agents[session_id], question.text, personality))
    save_question(session_id, question.text, response)
    return {"response": response, "session_id": session_id}


def create_session():
    session_id = uuid4()
    agents[session_id] = create_agent()
    return session_id


@app.post("/delete_session")
async def delete_session(session: Session):
    if session.session_id in agents:
        agents.pop(session.session_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
