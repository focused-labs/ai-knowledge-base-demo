from __future__ import print_function

import os
from datetime import datetime
from uuid import uuid4

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

PERSISTENCE_SPREADSHEET_ID = ''
PERSISTENCE_RANGE_NAME = 'Sheet1'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

service = None


def authenticate():
    creds = None
    if os.path.exists('service_account_token.json'):
        creds = Credentials.from_authorized_user_file('service_account_token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'service_account_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('service_account_token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def save_question(session_id, question, answer):
    try:
        creds = authenticate()
        append_values(creds, PERSISTENCE_SPREADSHEET_ID, PERSISTENCE_RANGE_NAME, "USER_ENTERED",
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
        append_values(creds, PERSISTENCE_SPREADSHEET_ID, PERSISTENCE_RANGE_NAME, "USER_ENTERED",
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
