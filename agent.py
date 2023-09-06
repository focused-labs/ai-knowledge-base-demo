import json

from langchain import PromptTemplate
from langchain.agents import ZeroShotAgent, Tool, ConversationalChatAgent, AgentExecutor
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory

from config import CHAT_MODEL
from tools.focused_labs_q_and_a_tool import create_vector_db_tool
from utils import format_quotes_in_json, is_answer_formatted_in_json, output_response


class Agent:

    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model_name=CHAT_MODEL)
        self.agent_executor = self.create_agent_executor()

    def create_agent_executor(self):
        q_and_a_tool = create_vector_db_tool(llm=self.llm)
        tools = [
            Tool(
                name="Focused Labs QA",
                return_direct=True,
                func=lambda query: _parse_source_docs(q_and_a_tool, query),
                description="useful for when you need to answer questions about Focused Labs"
            )
        ]

        prefix = """Have a conversation with a human, answering the following questions as best you can. You have 
        access to the following tools:"""
        suffix = """Begin!
    
        {chat_history}
        Question: {input}
        {agent_scratchpad}"""

        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )
        memory = ConversationSummaryBufferMemory(llm=self.llm, memory_key="chat_history", return_messages=True,
                                                 human_prefix="user", ai_prefix="assistant")
        custom_agent = ConversationalChatAgent.from_llm_and_tools(llm=self.llm,
                                                                  tools=tools,
                                                                  verbose=True,
                                                                  max_iterations=3,
                                                                  handle_parsing_errors=True,
                                                                  memory=memory,
                                                                  prompt=prompt
                                                                  )
        return AgentExecutor.from_agent_and_tools(agent=custom_agent, tools=tools, memory=memory,
                                                  verbose=True)

    def query_agent(self, user_input, personality="website visitor"):
        try:
            elaborate_prompt = get_prompt_template().format(
                query=user_input,
                personality=personality,
            )
            response = self.agent_executor.run(input=elaborate_prompt)
            if is_answer_formatted_in_json(response):
                return response
            return f"""
            {{
                "result": "{response}",
                "sources": "[]"
            }}"""

        except ValueError as e:
            response = str(e)
            response_prefix = "Could not parse LLM output: `\nAI: "
            if not response.startswith(response_prefix):
                raise e
            response_suffix = "`"
            if response.startswith(response_prefix):
                response = response[len(response_prefix):]
            if response.endswith(response_suffix):
                response = response[:-len(response_suffix)]
            output_response(response)
            return response


def get_prompt_template() -> PromptTemplate:
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


def _parse_source_docs(q_and_a_tool: RetrievalQA, query: str):
    result = q_and_a_tool({"question": query})
    formatted_result_string = format_quotes_in_json(result["result"])
    if 'source_documents' in result.keys():
        return f"""
            {{
            "result": "{formatted_result_string}",
            "sources": {json.dumps([i.metadata for i in result['source_documents']])}
            }}"""
    return f"""
        {{
        "result": "{formatted_result_string}",
        "sources": []
        }}"""
