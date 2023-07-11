from focused_labs_agent import FocusedLabsAgent
from importer import compose_graph
from utils import output_response


# Original prompt:
# system_prompt = '''
# You are a helpful virtual assistant for the employees of Focused Labs. Focused Labs is a boutique Software Consulting
# firm that specializes in enterprise application development and digital transformation. Employees will ask you
# Questions about the inner workings of the company. Questions could range in areas such as process, procedure, policy,
# and culture. Employees have different roles. The roles are either Developer, Designer, or Product Manager. The
# question is about how the company of Focused Labs operates. For each question, you need to capture their role.
#
# If they haven't provided their role, ask them for it.
# Think about this step by step:
# - The employee will ask a Question
# - You will ask them for their role within the company if they have not already provided it to you
# - Once you have their employee role, say "let me check on that for you...".
#
# Example:
#
# User: When is the 2023 Chicago IRL scheduled for?
#
# Assistant: That may depend on your role at Focused Labs. Are you a Developer, Designer, or Product Manager?
#
# User: I'm a developer.
#
# Assistant: Got it. Let me check on that for you...
# '''


# https://betterprogramming.pub/how-to-build-a-personalized-customer-service-llm-chatgpt-bot-eb4d1e373122
def create_lang_chain_chat_engine():

    assistant = FocusedLabsAgent(compose_graph())

    # while True:
    try:
        # if not init_conversation:
        #     user_input = input("Hi Am {} Buddy, Ask your question...".format(
        #         settings.COMPANY_NAME))
        #     init_conversation = True
        # else:
        #     user_input = input("Please ask your question...")
        user_input = input("Please ask your question...")
        agent_prompt = assistant.prompt_persona.format(
            query=user_input,
            company_name="Focused Labs",
            company_email="work@focusedlabs.io")
        response = assistant.agent({"input": agent_prompt})
        print(response)
        output_response(response["output"])
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
        # except KeyboardInterrupt:
        #     break
