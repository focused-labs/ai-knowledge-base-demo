import json
import os

import openai
import pinecone
from dotenv import load_dotenv
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.agents import ZeroShotAgent, Tool, initialize_agent, AgentType
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Pinecone

from config import PINECONE_INDEX, PINECONE_ENVIRONMENT, EMBEDDING_MODEL

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

llm = OpenAI(temperature=0)


def create_vector_db_tool():
    pinecone.init(
        api_key=os.getenv('PINECONE_API_KEY'),
        environment=PINECONE_ENVIRONMENT
    )
    text_field = "text"

    index = pinecone.Index(PINECONE_INDEX)

    embedding_model = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY
    )

    vectorstore = Pinecone(
        index, embedding_model.embed_query, text_field
    )
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        return_source_documents=True,
        input_key="question",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
    )


def parse_source_docs(qa, query):
    result = qa({"question": query})
    if 'source_documents' in result.keys():
        return f"""
        {{
        "result": "{result["result"]}",
        "sources": {json.dumps([i.metadata for i in result['source_documents']])}
        }}"""
    return f"""
    {{
    "result": "{result["result"]}",
    "sources": []
    }}"""


def create_agent_chain():
    qa = create_vector_db_tool()
    tools = [
        Tool(
            name="Focused Labs QA",
            return_direct=True,
            func=lambda query: parse_source_docs(qa, query),
            description="useful for when you need to answer questions about Focused Labs"
        )
    ]

    prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
    suffix = """Begin!"

    {chat_history}
    Question: {input}
    {agent_scratchpad}"""

    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"],
    )
    memory = ConversationBufferMemory(memory_key="chat_history")

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    return initialize_agent(
        tools,
        llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        llm_chain=llm_chain,
        max_iterations=3,
        handle_parsing_errors=True,
    )


def get_prompt_template() -> PromptTemplate:
    # TODO: Might want to tell the tool to always use the primary query engine to provide answers unless the question is about
    # itself or if it is about what was previously said in the conversation.? Just an idea!

    # Evaluate this question and see if it relates to Focused Labs. If so, answer this question with regards to
    # Focused Labs: {query}
    # If it does not relate to Focused Labs, then say "Hmm, I'm not sure."
    return PromptTemplate(
        template="""
                    You are a helpful virtual assistant for the employees of Focused Labs. 
                    
                    Think this through step by step.          
                    
                    If you don't know the answer, just say "Hmm, I'm not sure please contact work@focusedlabs.io  
                    for further assistance." Don't try to make up an answer.
                    
                    Please provide as detailed an answer as possible.
                    
                    When considering your answer, answer from the perspective of a {personality}.
        
                    Answer this question: {query}        
                    
                    """,
        input_variables=["query", "personality"],
    )
