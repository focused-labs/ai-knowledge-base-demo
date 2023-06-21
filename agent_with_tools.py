from langchain.chains.conversation.memory import ConversationBufferMemory
from llama_index import GPTVectorStoreIndex, download_loader, ListIndex, LLMPredictor, ServiceContext, \
    load_graph_from_storage
from langchain import OpenAI
from dotenv import load_dotenv
from importer import get_index_set
from llama_index.query_engine.transform_query_engine import TransformQueryEngine
from llama_index.indices.query.query_transform.base import DecomposeQueryTransform
from llama_index.langchain_helpers.agents import LlamaToolkit, create_llama_chat_agent, IndexToolConfig
from index_graph import IndexGraph

load_dotenv()


def create_graph_tool():
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, max_tokens=512))

    decompose_transform = DecomposeQueryTransform(
        llm_predictor, verbose=True
    )

    index_set = get_index_set()

    custom_query_engines = {}
    for index in index_set:
        query_engine = index.as_query_engine()
        query_engine = TransformQueryEngine(
            query_engine,
            query_transform=decompose_transform,
            transform_extra_info={'index_summary': index.index_struct.summary},
        )
        custom_query_engines[index.index_id] = query_engine
    custom_query_engines[IndexGraph.instance().graph.root_id] = IndexGraph.instance().graph.root_index.as_query_engine(
        response_mode='tree_summarize',
        verbose=True,
    )

    graph_query_engine = IndexGraph.instance().graph.as_query_engine(custom_query_engines=custom_query_engines)

    graph_config = IndexToolConfig(
        query_engine=graph_query_engine,
        name=f"Graph Index",
        description="useful for when you want to answer queries that require analyzing multiple SEC 10-K documents for Uber.",
        tool_kwargs={"return_direct": True}
    )

    return graph_config


def define_toolkit():
    index_set = get_index_set()

    index_configs = []

    notion_query_engine = index_set[0].as_query_engine(similarity_top_k=3, )
    notion_tool_config = IndexToolConfig(query_engine=notion_query_engine, name="Vector Index Notion",
                                         description="useful for when you want to answer questions located in notion",
                                         tool_kwargs={"return_direct": True})
    index_configs.append(notion_tool_config)
    web_scrape_query_engine = index_set[1].as_query_engine(similarity_top_k=3, )
    web_scrape_tool_config = IndexToolConfig(query_engine=web_scrape_query_engine, name="Vector Index Notion",
                                             description="useful for when you want to answer questions located on the "
                                                         "website",
                                             tool_kwargs={"return_direct": True})

    index_configs.append(web_scrape_tool_config)
    graph_config = create_graph_tool()

    toolkit = LlamaToolkit(index_configs=index_configs + [graph_config])
    return toolkit


def create_agent():
    toolkit = define_toolkit()

    memory = ConversationBufferMemory(memory_key="chat_history")
    llm = OpenAI(temperature=0)
    agent_chain = create_llama_chat_agent(
        toolkit,
        llm,
        memory=memory,
        verbose=True
    )
    return agent_chain
