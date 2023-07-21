import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chat_engine import create_lang_chain_chat_engine, query_lang_chain_chat_engine

allowed_origins = [
    "http://localhost:3000",
    "https://d3itb81et1oh8m.cloudfront.net",
    "https://fl-ai-knowledgehub-h27h6.ondigitalocean.app/"
]

query_engines = {}


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

    query_engines['focused_labs_agent'] = create_lang_chain_chat_engine()
    yield
    query_engines['doc_query_engine'] = None
    query_engines['focused_labs_agent'] = None


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
    personality = define_personality(question)
    response = query_lang_chain_chat_engine(query_engines['focused_labs_agent'], question.text, personality)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
