from langchain.chat_models import ChatOpenAI
from llama_index import LLMPredictor, ServiceContext


def get_llm_predictor():
    return LLMPredictor(llm=ChatOpenAI(temperature=0, max_tokens=512))


def get_service_context():
    llm_predictor_chatgpt = get_llm_predictor()
    return ServiceContext.from_defaults(llm_predictor=llm_predictor_chatgpt)
