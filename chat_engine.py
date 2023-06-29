from focused_labs_agent import FocusedLabsAgent
from llama_index import Prompt
from llama_index.chat_engine import CondenseQuestionChatEngine
from importer import compose_graph
from utils import get_service_context, output_response


# TODO: I removed the roles from the prompts for now...
def create_condense_question_chat_engine():
    custom_prompt = Prompt("""
    You are a helpful virtual assistant for the employees of Focused Labs. Focused Labs is a boutique Software 
    Consulting firm that specializes in enterprise application development and digital transformation. 
    Employees will ask you Questions about the inner workings of the company. Questions could range in areas such 
    as process, procedure, policy, and culture. 
            
    Think about this step by step:
    - The employee will ask a Question
    - Once they ask a question, say "let me check on that for you...".

    Example:
    
    User: When is the 2023 Chicago IRL scheduled for?
    
    Assistant: Let me check on that for you...
    Given a conversation (between Human and Assistant) and a follow up message from Human, 
    rewrite the message to be a standalone question that captures all relevant context 
    from the conversation.
    
    <Chat History> 
    {chat_history}
    
    <Follow Up Message>
    {question}
    
    <Standalone question>
    """)

    custom_chat_history = [
        (
            'Hello assistant, we are having a insightful discussion about Focused Labs today.',
            'Okay, sounds good.'
        )
    ]

    return CondenseQuestionChatEngine.from_defaults(
        query_engine=compose_graph(),
        condense_question_prompt=custom_prompt,
        chat_history=custom_chat_history,
        service_context=get_service_context(),
        verbose=True
    )


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
        response = assistant.agent.run(agent_prompt)
        output_response(response)
    except ValueError as e:
        response = str(e)
        response_prefix = "Could not parse LLM output: `"
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
