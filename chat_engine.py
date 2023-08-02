from agent import create_agent_chain, get_prompt_template
from utils import output_response


def create_agent():
    return create_agent_chain()


def create_interactive_agent():
    agent = create_agent()
    user_input = input("Please ask your question...")
    return query_agent(agent, user_input)


def query_agent(agent, user_input, personality="website visitor"):
    try:
        elaborate_prompt = get_prompt_template().format(
            query=user_input,
            personality=personality,
        )
        response = agent.run(input=elaborate_prompt)
        return response
    except ValueError as e:
        response = str(e)
        response_prefix = "Could not parse LLM output: "
        if not response.startswith(response_prefix):
            raise e
        response_suffix = "`"
        if response.startswith(response_prefix):
            response = response[len(response_prefix):]
        if response.endswith(response_suffix):
            response = response[:-len(response_suffix)]
        output_response(response)
        return response
