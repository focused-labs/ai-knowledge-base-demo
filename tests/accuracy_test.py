import json

from chat_engine import create_agent, query_agent
from main import create_session
from persistence import save_question, save_error


def accuracy_test(spreadsheet_id, spreadsheet_range, question):
    session_id = create_session()
    agent = create_agent()
    try:
        answer = query_agent(agent, question).replace("\n", "")
        response_formatted = json.loads(answer)
        save_question(session_id, question, response_formatted, spreadsheet_id, spreadsheet_range)
    except Exception as e:
        save_error(session_id, question, str(e), spreadsheet_id, spreadsheet_range)
        raise e
