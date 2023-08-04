# Focused Labs Knowledge Hub

This a starter repo that builds a basic Knowledge Hub and then uses FastAPI to expose it to a UI. 



## Getting this running...

### Create `.env` file
- Create a file at the root of the project named `.env`
- Add the following: 
```
OPENAI_API_KEY = "<retrieve value from 1password 'Special Projects or R&D' Vault - Open AI API Token Secure Note>"
NOTION_API_KEY = "<retrieve value from 1password 'Special Projects or R&D' Vault - Notion API Token Secure Note>"
GITHUB_TOKEN = "<set up your own github account using your focusedlabs email, and create a token>"
PINECONE_API_KEY = "<retrieve value from 1password 'Special Projects or R&D' Vault - Pinecone DB credential>"
```

### Pinecone Dashboard Access
To view the Pinecone Database dashboard, create an account with Pinecone. Then, ask a teammate to add you to the Focused Labs Knowledge Base Hub project. 

### Start the API
Run
```
 uvicorn main:app
```
Add `--reload` if you make a code change the app will restart on its own.

#### References for now
https://platform.openai.com/docs/tutorials/web-qa-embeddings

To see the last commit that uses Redis as the vector database and uses the Composable graph, 
pull the git commit at `bd9a3037ad417d0e1af1e77e251fe532d09ddffc`.