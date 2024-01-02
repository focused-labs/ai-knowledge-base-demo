import os
import pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.pinecone import Pinecone
from config import PINECONE_ENVIRONMENT, PINECONE_INDEX


def _init_pinecone():
    pinecone.init(
        api_key=os.getenv('PINECONE_API_KEY'),
        environment=PINECONE_ENVIRONMENT
    )
    index_name = PINECONE_INDEX
    if index_name not in pinecone.list_indexes():
        print("Could not find index in pinecone! Creating a new one")
        pinecone.create_index(name=index_name, metric="cosine", dimension=1536)

    embeddings = OpenAIEmbeddings()
    return Pinecone.from_existing_index(index_name, embeddings)


class PineconeManager:
    def __init__(self):
        self.vectorstore = _init_pinecone()
