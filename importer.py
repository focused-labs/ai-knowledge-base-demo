from langchain.chat_models import ChatOpenAI
from llama_index.indices.query.query_transform import DecomposeQueryTransform
from llama_index.query_engine import TransformQueryEngine

from llama_index import NotionPageReader
import os
from dotenv import load_dotenv
from transformers import normalize_text
from llama_index import GPTVectorStoreIndex, download_loader, LLMPredictor, ServiceContext
from llama_index.vector_stores import RedisVectorStore
from llama_index.storage.storage_context import StorageContext
from index_graph import IndexGraph

load_dotenv()
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
integration_token = NOTION_API_KEY
NOTION_INDEX_NAME = "notion-fl-index"
NOTION_PREFIX = "notionfocusedlabsdocs"
WEB_SCRAPE_INDEX_NAME = "web-scrape-fl-index"
WEB_SCRAPE_PREFIX = "webscrapefocusedlabsdocs"

page_ids = [
    "40b801917ab04deb8f5759d9d3e2da59",  # The Chicago Office
    "64c61657f90b48f786e8b55098f26e3a",  # Denver Lightning Talks
    # "76d816d82434423d8fbec83a3979d245",  # AI Knowledge Base
    "642768dbfd6041e699a24b2863fab5b2",  # Denver IRL Agenda
    "9f45258c6cab4592badeec6f1060e5df",  # Pairing
    "c4e0d82f59d444c486066205919e2088",  # Why we do what we do
    "5b25eda9934745fa8e9dd4bbf131eabc",  # Chicago IRL Logistics
    "4747650f9fd74f9b9d43e817963d6759",  # Denver IRL Logistics
    "53f3ff1456ea4c298e70281902080d9f",  # Pairing Interview
    "f621f275876945dcab7a298d21fb95c4",  # Denver Family Friend Day
    "2bcdac9fedd14404ba85a47323f5a1ad",  # Tech Lead
    "87d80ebf66c64422a21570b5c2d0b0bc",  # Daily Company Stand up
    "a255954246c44ab1a6178f54f1095b41",  # Pair Retros
    "0050c37a71464a73ab77e01a5ab5a76d",  # Project Rotations
    "6977e3c091384b1abe1f1692fce9995f",  # 2023 Strategy
    "ff2478fce704496d85462d8c8656f074",  # The Denver Office
    "d30c87af7d60458aaf7fb412d422a691",  # 2023 Chicago IRL
    "690037a4c2a64688b43303bc4d2a65d0",  # Product Design Lunch
    "5ade11d0a39342129580364d35106eee",  # Ski Weekend
    "50901371968b4dbb9423186c7cd392dc",  # Software Development - Issues?
    "dc8864d18f7c4c1595c2e278d36743c4",  # So you want to be a TPIer?
    "447552ca7fec4e2fa568cb918d166c42",  # Anchors - Issues?
    "94f952deb00740929e9b526f93609c46",  # Denver activities and meals
    "8ea1eccd201842c28f9cd709b95754a1"]  # Chicago IRL Agenda

llm_predictor_chatgpt = LLMPredictor(llm=ChatOpenAI(temperature=0, max_tokens=512))
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor_chatgpt)

def import_data():
    pass


def import_notion_data():
    documents = NotionPageReader(integration_token=integration_token).load_data(page_ids=page_ids)

    # checks for duplicates in the document list by id
    # ids = [document.doc_id for document in documents]
    # seen = set()
    # dupes = [x for x in ids if x in seen or seen.add(x)]
    # print(seen)
    # print(dupes)

    for document in documents:
        document.text = normalize_text(document.text)

    vector_store = get_vector_store(NOTION_INDEX_NAME, NOTION_PREFIX)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = GPTVectorStoreIndex.from_documents(documents, storage_context=storage_context,
                                               service_context=service_context)
    return index


def number_of_stored_notion_docs():
    vector_store = get_vector_store(NOTION_INDEX_NAME, NOTION_PREFIX)
    redis_client = vector_store.client
    return len(redis_client.keys())


def import_web_scrape_data():
    BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")

    loader = BeautifulSoupWebReader()
    documents = loader.load_data(
        urls=['https://focusedlabs.io', 'https://focusedlabs.io/about', 'https://focusedlabs.io/contact',
              'https://focusedlabs.io/case-studies',
              "https://focusedlabs.io/case-studies/agile-workflow-enabled-btr-automation",
              "https://focusedlabs.io/case-studies/hertz-technology-new-markets",
              "https://focusedlabs.io/case-studies/aperture-agile-transformation",
              "https://focusedlabs.io/case-studies/automated-core-business-functionality"])

    # print(documents)

    for document in documents:
        document.text = normalize_text(document.text)

    vector_store = get_vector_store(WEB_SCRAPE_INDEX_NAME, WEB_SCRAPE_PREFIX)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = GPTVectorStoreIndex.from_documents(documents, storage_context=storage_context,
                                               service_context=service_context)
    return index


def number_of_stored_web_scrape_docs():
    vector_store = get_vector_store(WEB_SCRAPE_INDEX_NAME, WEB_SCRAPE_PREFIX)
    redis_client = vector_store.client
    return len(redis_client.keys())


def compose_graph():
    # describe each index to help traversal of composed graph
    index_summaries = ["Focused Labs internal knowledge from Notion",
                       "Focused Labs public knowledge scraped from website"]
    index_name = ["Notion_Documents", "Website_Documents"]
    index_set = get_index_set()

    index_graph = IndexGraph(index_set, index_summaries)
    decompose_transform = DecomposeQueryTransform(
        llm_predictor_chatgpt, verbose=True
    )

    custom_query_engines = {}
    for i, index in enumerate(index_set):
        query_engine = index.as_query_engine(service_context=service_context)
        transform_extra_info = {'index_summary': index_summaries[i]}
        transformed_query_engine = TransformQueryEngine(query_engine, decompose_transform,
                                                        transform_extra_info=transform_extra_info)
        custom_query_engines[index_name[i]] = transformed_query_engine

    custom_query_engines[index_graph.graph.root_index.index_id] = index_graph.graph.root_index.as_query_engine(
        retriever_mode='simple',
        response_mode='tree_summarize',
        service_context=service_context
    )

    return index_graph.graph.as_query_engine(custom_query_engines=custom_query_engines)


def get_specific_index(index_name, prefix_name):
    vector_store = get_vector_store(index_name, prefix_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = GPTVectorStoreIndex([], storage_context=storage_context)
    return index


def get_index_set():
    notion_index = get_specific_index(NOTION_INDEX_NAME, NOTION_PREFIX)
    web_scrape_index = get_specific_index(WEB_SCRAPE_INDEX_NAME, WEB_SCRAPE_PREFIX)

    index_set = [notion_index, web_scrape_index]
    return index_set


def get_vector_store(index_name, prefix_name):
    return RedisVectorStore(
        index_name=index_name,
        index_prefix=prefix_name,
        redis_url="redis://localhost:6379",
        overwrite=True,
    )
