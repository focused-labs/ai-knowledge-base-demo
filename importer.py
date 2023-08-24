import json

from pinecone_database import get_pinecone_storage_context
from llama_index import NotionPageReader, VectorStoreIndex, download_loader
import os
from dotenv import load_dotenv
from custom_transformers import normalize_text
from utils import get_service_context
import http.client

load_dotenv()
NOTION_API_KEY = os.getenv('NOTION_API_KEY')

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


def import_notion_data(page_ids):
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


def import_web_scrape_data(urls: list):
    BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")

    loader = BeautifulSoupWebReader()
    documents = loader.load_data(urls=urls)

    for document in documents:
        document.text = normalize_text(document.text)

    index = VectorStoreIndex.from_documents(documents,
                                            storage_context=get_pinecone_storage_context(),
                                            service_context=get_service_context())
    return index
