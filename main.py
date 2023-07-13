import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chat_engine import create_lang_chain_chat_engine, query_lang_chain_chat_engine
from importer import number_of_stored_notion_docs, number_of_stored_web_scrape_docs, \
    compose_graph

allowed_origins = [
    "http://localhost:3000",
]

query_engines = {}


def init_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


def load_notion_documents():
    print("Loading notion docs")
    # TODO only drop the index if it exists
    # redis_client = get_redis_connection()
    # redis_client.ft(NOTION_INDEX_NAME).dropindex()
    # import_notion_data()
    print("Number of stored notion docs: ", number_of_stored_notion_docs())


def load_web_scrape_documents():
    print("Loading web scraped docs")
    # TODO only drop the index if it exists
    # redis_client = get_redis_connection()
    # redis_client.ft(WEB_SCRAPE_INDEX_NAME).dropindex()
    # import_web_scrape_data()
    print("Number of store web scraped docs: ", number_of_stored_web_scrape_docs())


class Question(BaseModel):
    text: str
    role: str


prompt_intros = {
    "none": "",
    "developer": "You are an expert software engineer. ",
    "designer": "You are an expert UX / UI designer. ",
    "pm": "You are an expert product manager.",
    "executive": "You are an executive at a successful company. ",
    "client": "You are evaluating Focused Labs as a potential partner. "
}


def expand_prompt(question: Question):
    if question.role is None:
        question.role = "none"
    prompt = prompt_intros[question.role]
    return prompt + "At Focused Labs, " + question.text + " Carefully consider your answer before responding."


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logging()

    # Load documents. This can be slow so block the API until ready
    load_notion_documents()
    load_web_scrape_documents()

    # Build a graph from the indexes just created and store its query engine
    # query_engines['doc_query_engine'] = compose_graph()
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
    # prompt = expand_prompt(question)
    # print(prompt)
    response = query_lang_chain_chat_engine(query_engines['focused_labs_agent'], question.text)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
