# Focused Labs Knowledge Hub

This a starter repo that builds a basic Knowledge Hub and then uses FastAPI to expose it to a UI. 

## Getting this running...

### Install Redis

Install docker, start it, and run `docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:6.2.6`

### Create `.env` file
- Create a file at the root of the project named `.env`
- Add the following: 
```
OPENAI_API_KEY = "<retrieve value from 1password 'Special Projects or R&D' Vault - Open AI API Token Secure Note>"
NOTION_API_KEY = "<retrieve value from 1password 'Special Projects or R&D' Vault - Notion API Token Secure Note>"
GITHUB_TOKEN = "<set up your own github account using your focusedlabs email, and create a token>"
```

### Start the API
Run
```
 uvicorn main:app --reload
```
The reload means if you make a code change the app will restart on its own.

