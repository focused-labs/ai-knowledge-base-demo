from langchain import PromptTemplate
from langchain.agents import initialize_agent, Tool, AgentType, AgentExecutor
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from llama_index.indices.query.base import BaseQueryEngine

from config import CHAT_MODEL


class FocusedLabsAgent(object):

    def __init__(self,  data_source: BaseQueryEngine):
        if not isinstance(data_source, BaseQueryEngine):
            raise TypeError("data_source must be an instance of BaseQueryEngine")
        self._graph = data_source
        self.llm = ChatOpenAI(
            model_name=CHAT_MODEL,
            temperature=0
        )
        self.tools = [
            Tool(
                name="Focused Labs Domain Data Graph",
                func=lambda q: str(self.graph.query(q)),
                description="""
                useful for when you want to answer questions from Focused Labs Domain Data Graph. Always, 
                you must try the graph first, only answer based this Focused Labs Domain Data Graph
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
        return PromptTemplate(
            template="""
            You are a personal assistant for {company_name} company your job is to answer questions. 
            Use only context Focused Labs Domain Data Graph to provide answers.
            Do not provide any answers that deviate from your tools documents.
            If you don't know the answer, just say "Hmm, Im not sure please contact customer support at {company_email} 
            for further assistance." Don't try to make up an answer.:
            --------
            Question: Answer with regards to Focused Labs {query}
            """,
            input_variables=["query", "company_name", "company_email"],
        )

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, value):
        self._graph = value
