# Focused Labs Knowledge Hub

This a starter repo that builds a basic Knowledge Hub and then uses FastAPI to expose it to a UI.

## Getting this running...

### Logging

- The python logs can be viewed in production on the Digital Ocean `Apps` > `Runtime Logs` tab, or on the console when
  running locally.
- For user questions and answers, since we don't have a database (yet) we spun up a simple solution using the Google
  Sheets API
- A sheet in production logs all questions, answers, sources and error messages.
- On your local machine, you should create your own google sheet for logging following the instructions for `.env`
  below.

### Create `.env` file

- Ask a teammate for the URL of the google sheet `Chat History` in prod
- From the File menu, choose `Make a Copy`. Locate the copy in `My Drive`. (only you have access)
- Keeping the header row, clear all the data from your local sheet
- Locate the sheet id from the URL of your local sheet, for example for URL

```
https://docs.google.com/spreadsheets/d/123/edit#gid=0
the sheet id is 123
```

- Copy `template.env` into a file at the root of the project named `.env`

```
OPENAI_API_KEY = "<retrieve value from 1password 'Special Projects or R&D' Vault - Open AI API Token Secure Note>"
NOTION_API_KEY = "<retrieve value from 1password 'Special Projects or R&D' Vault - Notion API Token Secure Note>"
GITHUB_TOKEN = "<set up your own github account using your focusedlabs email, and create a token>"
PINECONE_API_KEY = "<retrieve value from 1password 'Special Projects or R&D' Vault - Pinecone DB DEV credential>"
GOOGLE_API_SPREADSHEET_ID = 'your local spreadsheet id'
GOOGLE_API_RANGE_NAME = 'Sheet1'
GOOGLE_CREDS_TOKEN = '<get this from 1password>'
```

- Copy in values from the local sheet id as explained above, and from 1password in the `Special Projects` vault for the
  google values.

### Pinecone Dashboard Access

To view the Pinecone Database dashboard, create an account with Pinecone. Then, ask a teammate to add you to the Focused
Labs Knowledge Base Hub project.

### Start the API

Run

```
 uvicorn main:app
```

Add `--reload` if you make a code change the app will restart on its own.

### Run accuracy test
Cannot be run via command line.

Edit the run configuration for `accuracy_test_runner.py` and add the file that contains the list of questions you want
to ask. Ex: `questions.txt`

#### References for now

https://platform.openai.com/docs/tutorials/web-qa-embeddings

##   

If you need to change the permissions of the google api credentials for whatever reason, then you will need to
regenerate a new token.

1. You will need run the code locally, without any existing valid credentials. This should force the code to initiate a
   manual browser login and verification.
2. Add `service_account_credentials.json` file to your local file system. You can find this in 1pass.
3. Run `accuracy_test_runner.py`
4. You will then need to take the token that is generated (printed in console) and
   update the `GOOGLE_CREDS_TOKEN` environment variable.