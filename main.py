import logging
import sys
from contextlib import asynccontextmanager
from uuid import uuid4

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from import_service import import_web_scrape_data, import_notion_data
from models.imported_pages import ImportedPages
from models.imported_urls import ImportedUrls
from models.question import Question
from models.session import Session
from query_service import QueryService

load_dotenv()

allowed_origins = [
    "http://localhost:3000",
    "https://fl-ai-knowledgehub-h27h6.ondigitalocean.app/",
    "https://dev-kb-xxl7y.ondigitalocean.app/",
    "https://chat.withfocus.com/",
    "https://chat.focusedlabs.io/"
]

query_service = QueryService()


def init_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))



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
    question.role = define_personality(question)
    return query_service.query(question=question)


@app.post("/delete_session")
async def delete_session(session: Session):
    query_service.delete_query_session(session)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
