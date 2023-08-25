import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Optional
from uuid import uuid4, UUID

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chat_engine import create_agent, query_agent
from importer import import_web_scrape_data, import_notion_data
from persistence import save_question, save_error

load_dotenv()

allowed_origins = [
    "http://localhost:3000",
    "https://fl-ai-knowledgehub-h27h6.ondigitalocean.app/",
    "https://dev-kb-xxl7y.ondigitalocean.app/",
    "https://chat.withfocus.com/",
    "https://chat.focusedlabs.io/"
]

agents = {}


def init_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


class Question(BaseModel):
    text: str
    role: str
    session_id: Optional[UUID]


class ImportedPages(BaseModel):
    page_ids: list


class ImportedUrls(BaseModel):
    page_urls: list


class Session(BaseModel):
    session_id: UUID


personalities = {
    "none": "website visitor",
    "candidate": "potential employee",
    "client": "potential client",
    "customer": "potential customer"
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

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/load-notion-docs")
def load_notion_documents(imported_pages: ImportedPages):
    print(f"Loading the following notion docs {imported_pages}")
    import_notion_data(imported_pages.page_ids)
    return {"status": "Notion Docs Loaded"}


@app.post("/load-website-docs")
def load_web_scrape_documents(website: ImportedUrls):
    print(f"Loading following web scraped docs {website.page_urls}")
    import_web_scrape_data(website.page_urls)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/query/")
async def query(question: Question):
    session_id = question.session_id
    if session_id not in agents:
        session_id = create_session()
    personality = define_personality(question)
    try:
        answer = query_agent(agents[session_id], question.text, personality).replace("\n", "")
        response_formatted = json.loads(answer)
        save_question(session_id, question.text, response_formatted, os.getenv("GOOGLE_API_SPREADSHEET_ID"),
                      os.getenv("GOOGLE_API_RANGE_NAME"))
        return {"response": response_formatted, "session_id": session_id}
    except Exception as e:
        error = save_error(session_id, question.text, str(e), os.getenv("GOOGLE_API_SPREADSHEET_ID"), os.getenv("GOOGLE_API_RANGE_NAME"))
        raise e


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
