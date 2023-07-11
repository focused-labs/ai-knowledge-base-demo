from llama_index.vector_stores import RedisVectorStore
from llama_index import StorageContext, GPTVectorStoreIndex
from redis import Redis

from config import NOTION_INDEX_NAME, NOTION_PREFIX, WEB_SCRAPE_INDEX_NAME, \
    WEB_SCRAPE_PREFIX


def get_specific_index(index_name, prefix_name):
    storage_context = get_storage_context(index_name, prefix_name)
    index = GPTVectorStoreIndex([], storage_context=storage_context)
    return index


def get_index_set():
    notion_index = get_specific_index(NOTION_INDEX_NAME, NOTION_PREFIX)
    web_scrape_index = get_specific_index(WEB_SCRAPE_INDEX_NAME, WEB_SCRAPE_PREFIX)

    index_set = [notion_index, web_scrape_index]
    return index_set


def get_storage_context(index_name, prefix_name):
    vector_store = get_vector_store(index_name, prefix_name)
    return StorageContext.from_defaults(vector_store=vector_store)


def get_vector_store(index_name, prefix_name):
    return RedisVectorStore(
        index_name=index_name,
        index_prefix=prefix_name,
        redis_url="redis://localhost:6379",
        overwrite=True,
    )


# Get a Redis connection
def get_redis_connection(host='localhost', port='6379', db=0):
    r = Redis(host=host, port=port, db=db, decode_responses=False)
    return r
