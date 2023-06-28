from llama_index import Prompt
from llama_index.chat_engine import CondenseQuestionChatEngine
from importer import compose_graph
from utils import get_service_context


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

    # tool1 = QueryEngineTool.from_defaults(
    #     query_engine=compose_graph(),
    #     description="Use this query engine to find information about Focused Labs. This information includes: the "
    #                 "kind of work Focused Labs produces, information about how the company works, "
    #                 "employee information, project information, marketing materials, and case studies.",
    # )

    # return ReActChatEngine.from_query_engine(
    #     query_engine=compose_graph(),
    #     name="Focused Labs Chat",
    #     description="Use this query engine to find information about Focused Labs. This information includes: the "
    #                 "kind of work Focused Labs produces, information about how the company works, "
    #                 "employee information, project information, marketing materials, and case studies.",
    #     service_context=service_context,
    #     verbose=True
    # )

    return CondenseQuestionChatEngine.from_defaults(
        query_engine=compose_graph(),
        condense_question_prompt=custom_prompt,
        chat_history=custom_chat_history,
        service_context=get_service_context(),
        verbose=True
    )