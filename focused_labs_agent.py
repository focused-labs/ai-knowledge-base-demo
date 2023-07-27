import os

import openai
from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.agents import initialize_agent, Tool, AgentType, AgentExecutor
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from llama_index.indices.query.base import BaseQueryEngine

from config import CHAT_MODEL
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

class FocusedLabsAgent(object):

    def __init__(self, data_source: BaseQueryEngine):
        if not isinstance(data_source, BaseQueryEngine):
            raise TypeError("data_source must be an instance of BaseQueryEngine")
        self._primary_query_engine = data_source
        self.llm = ChatOpenAI(
            model_name=CHAT_MODEL,
            temperature=0
        )
        self.tools = [
            Tool(
                name="Focused Labs Domain Data",
                func=lambda q: str(
                    self.primary_query_engine.query("Answer with regards to Focused Labs: " + q)
                ),
                description="""
                useful for when you want to answer questions from Focused Labs Domain Data. Always, 
                you must try this tool first, only answer based on this Focused Labs Domain Data
                """,
            )
        ]

    @property
    def memory(self) -> ConversationBufferMemory:
        return ConversationBufferMemory(memory_key="chat_history",
                                        input_key="input",
                                        output_key="output",
                                        return_messages=True)

    @property
    def agent(self) -> AgentExecutor:
        return initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=10
        )

    @property
    def prompt_persona(self) -> PromptTemplate:
        # TODO: Might want to tell the tool to always use the primary query engine to provide answers unless the question is about
        # itself or if it is about what was previously said in the conversation.? Just an idea!
        return PromptTemplate(
            template="""
            You are a helpful virtual assistant for the employees of {company_name}. Focused Labs is a boutique Software 
            Consulting firm that specializes in enterprise application development and digital transformation. 
            Employees will ask you Questions about the inner workings of the company. Questions could range in areas 
            such as process, procedure, policy, and culture. 
            Use only context Focused Labs Domain Data to provide answers.
            
            Think this through step by step.          
            
            If you don't know the answer, just say "Hmm, Im not sure please contact customer support at {company_email} 
            for further assistance." Don't try to make up an answer.
            
            Please provide as detailed an answer as possible.
            
            When considering your answer, answer from the perspective of a {personality}.

            Evaluate this question and see if it relates to Focused Labs. If so, answer this question with regards to 
            Focused Labs: {query}            
            
            If it does not relate to Focused Labs, then say "Hmm, I'm not sure."
            
            """,
            input_variables=["query", "company_name", "company_email", "personality"],
        )

    @property
    def primary_query_engine(self):
        return self._primary_query_engine

    @primary_query_engine.setter
    def primary_query_engine(self, value):
        self._primary_query_engine = value
