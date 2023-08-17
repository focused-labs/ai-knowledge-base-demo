from __future__ import print_function

import os
from datetime import datetime
from uuid import uuid4

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


load_dotenv()

service = None


def authenticate():
    user_info = {
        "client_id": os.getenv("GOOGLE_API_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_API_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_API_REFRESH_TOKEN"),
        "expiry": os.getenv("GOOGLE_API_EXPIRY")
    }
    creds = Credentials.from_authorized_user_info(user_info, ['https://www.googleapis.com/auth/spreadsheets'])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            os.environ["GOOGLE_API_EXPIRY"] = creds.expiry.strftime("%Y-%m-%dT%H:%M:%S")
    return creds


def save_question(session_id, question, answer):
    try:
        creds = authenticate()
        append_values(creds, os.getenv("GOOGLE_API_SPREADSHEET_ID"), os.getenv("GOOGLE_API_RANGE_NAME"), "USER_ENTERED",
                  [
                      [
                          str(datetime.utcnow()),
                          str(session_id),
                          question,
                          answer["result"],
                          "\n".join([i['URL'] for i in answer["sources"]])
                      ]
                  ])
    except Exception as e:
        print(f"Error returned from google authentication: {e}")


def save_error(session_id, question, message):
    try:
        creds = authenticate()
        append_values(creds, os.getenv("GOOGLE_API_SPREADSHEET_ID"), os.getenv("GOOGLE_API_RANGE_NAME"), "USER_ENTERED",
                  [
                      [
                          str(datetime.utcnow()),
                          str(session_id),
                          question,
                          "",
                          "",
                          message
                      ]
                  ])
    except Exception as e:
        print(f"Error returned from google authentication: {e}")


def append_values(creds, spreadsheet_id, range_name, value_input_option, values):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
        """
    try:
        service = build('sheets', 'v4', credentials=creds)

        body = {
            'values': values
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        # print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


if __name__ == '__main__':
    save_question(uuid4(), "Where is the chicago office?", "I think it's on Tattooine")
