import streamlit as st
from streamlit_chat import message

from database import get_redis_connection
from chatbot import RetrievalAssistant, Message

# Initialise database

## Initialise Redis connection
redis_client = get_redis_connection()

# Set instruction

system_prompt = '''
You are a helpful virtual assistant for the employees of Focused Labs. Focused Labs is a boutique Software Consulting firm that specializes in enterprise application development and digital transformation. Employees will ask you Questions about the inner workings of the company. Questions could range in areas such as process, procedure, policy, and culture. Employees have different roles. The roles are either Developer, Designer, or Product Manager. The question is about how the company of Focused Labs operates. For each question, you need to capture their role.
If they haven't provided their role, ask them for it.
Think about this step by step:
- The employee will ask a Question
- You will ask them for their role within the company if they have not already provided it to you
- Once you have their employee role, say "let me check on that for you...".

Example:

User: When is the 2023 Chicago IRL scheduled for?

Assistant: That may depend on your role at Focused Labs. Are you a Developer, Designer, or Product Manager?

User: I'm a developer.

Assistant: Got it. Let me check on that for you...
'''

### CHATBOT APP

st.set_page_config(
    page_title="Focused Labs AI Assistant",
    page_icon=":robot:"
)

st.title('Focused Labs Chatbot')
st.subheader("Here to answer your questions about working at Focused Labs")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []


def query(question):
    response = st.session_state['chat'].ask_assistant(question)
    return response


prompt = st.text_input("What do you want to know: ", "", key="input")

if st.button('Submit', key='generationSubmit'):

    # Initialization
    if 'chat' not in st.session_state:
        st.session_state['chat'] = RetrievalAssistant()
        messages = []
        system_message = Message('system', system_prompt)
        messages.append(system_message.message())
    else:
        messages = []

    user_message = Message('user', prompt)
    messages.append(user_message.message())

    response = query(messages)

    # Debugging step to print the whole response
    # st.write(response)

    st.session_state.past.append(prompt)
    st.session_state.generated.append(response['content'])

if st.session_state['generated']:

    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
