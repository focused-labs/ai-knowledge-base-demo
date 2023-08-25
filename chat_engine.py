import json

from agent import create_agent_chain, get_prompt_template
from utils import output_response


def create_agent():
    return create_agent_chain()


def create_interactive_agent():
    agent = create_agent()
    user_input = input("Please ask your question...")
    return query_agent(agent, user_input)


def is_answer_formatted_in_json(answer):
    try:
        json.loads(answer)
        return True
    except ValueError as e:
        return False


def query_agent(agent, user_input, personality="website visitor"):
    try:
        elaborate_prompt = get_prompt_template().format(
            query=user_input,
            personality=personality,
        )
        response = agent.run(input=elaborate_prompt)
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
