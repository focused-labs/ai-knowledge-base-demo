from uuid import uuid4

from chain import Chain
from logger import save_question, save_error
from pinecone_manager import PineconeManager


def accuracy_test(spreadsheet_id, question):
    chain = Chain(vector_store=PineconeManager().vectorstore)
    try:
        result = chain.complete_chain.invoke(
            {"question": question, "session_id": str(uuid4()), "role": "human"})
        answer = result["answer"].content
        sources = []
        for doc in result["docs"]:
            source_url = doc.metadata['URL']
            sources.append({"URL": source_url})

        response_formatted = {"result": answer, "sources": sources}
        save_question(question=question, answer=response_formatted, sheet_id=spreadsheet_id)
    except Exception as e:
        save_error(question, str(e), spreadsheet_id)
        raise e
