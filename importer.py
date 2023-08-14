import json


from pinecone_database import get_pinecone_storage_context
from llama_index import NotionPageReader, VectorStoreIndex, download_loader
import os
from dotenv import load_dotenv
from custom_transformers import normalize_text
from utils import get_service_context, get_llm_predictor
import http.client

load_dotenv()
NOTION_API_KEY = os.getenv('NOTION_API_KEY')

page_ids = [
    "40b801917ab04deb8f5759d9d3e2da59",  # The Chicago Office
    "64c61657f90b48f786e8b55098f26e3a",  # Denver Lightning Talks
    "76d816d82434423d8fbec83a3979d245",  # AI Knowledge Base
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
    "50901371968b4dbb9423186c7cd392dc",  # Software Development
    "dc8864d18f7c4c1595c2e278d36743c4",  # So you want to be a TPIer?
    "447552ca7fec4e2fa568cb918d166c42",  # Anchors
    "94f952deb00740929e9b526f93609c46",  # Denver activities and meals
    "8ea1eccd201842c28f9cd709b95754a1"]  # Chicago IRL Agenda

page_titles = [{}]


def get_notion_metadata(page_id):
    try:
        headers = {'Authorization': f'Bearer {NOTION_API_KEY}', 'Notion-Version': '2022-06-28'}
        connection = http.client.HTTPSConnection("api.notion.com")

        connection.request("GET", f"/v1/pages/{page_id}/properties/title", headers=headers)
        page_title = json.loads(connection.getresponse().read())

        connection.request("GET", f"/v1/pages/{page_id}", headers=headers)
        page_url = json.loads(connection.getresponse().read())

        return {"page_title": page_title['results'][0]['title']['plain_text'], "page_url": page_url['url']}
    except Exception as e:
        print(f"Failed to retrieve notion metadata{e} for page id: {page_id}")
        return {"page_title": "", "page_url": ""}


def import_notion_data():
    documents = NotionPageReader(integration_token=NOTION_API_KEY).load_data(page_ids=page_ids)
    for document in documents:
        document_metadata = get_notion_metadata(page_id=document.extra_info["page_id"])
        url = document_metadata['page_url']
        title = document_metadata['page_title']
        document.extra_info.update({"URL": url, "title": title})
        document.metadata = ({"URL": url, "title": title})
        document.text = normalize_text(document.text)

    index = VectorStoreIndex.from_documents(documents,
                                            storage_context=get_pinecone_storage_context(),
                                            service_context=get_service_context())
    return index


def import_web_scrape_data():
    BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")

    loader = BeautifulSoupWebReader()
    documents = loader.load_data(
        urls=['https://focusedlabs.io',
              'https://focusedlabs.io/about',
              'https://focusedlabs.io/contact',
              'https://focusedlabs.io/case-studies',
              "https://focusedlabs.io/case-studies/agile-workflow-enabled-btr-automation",
              "https://focusedlabs.io/case-studies/hertz-technology-new-markets",
              "https://focusedlabs.io/case-studies/aperture-agile-transformation",
              "https://focusedlabs.io/case-studies/automated-core-business-functionality"])

    for document in documents:
        document.text = normalize_text(document.text)

    index = VectorStoreIndex.from_documents(documents,
                                            storage_context=get_pinecone_storage_context(),
                                            service_context=get_service_context())
    return index
