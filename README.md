# Powering your products with ChatGPT and your own data

The Chatbot Kickstarter is a starter repo to get you used to building basic a basic Chatbot using the ChatGPT API and your own knowledge base. The flow you're taken through was originally presented with [these slides](https://drive.google.com/file/d/1dB-RQhZC_Q1iAsHkNNdkqtxxXqYODFYy/view?usp=share_link), which may come in useful to refer to. 

This repo contains one notebook and two basic Streamlit apps:
- `powering_your_products_with_chatgpt_and_your_data.ipynb`: A notebook containing a step by step process of tokenising, chunking and embedding your data in a vector database, and building simple Q&A and Chatbot functionality on top.
- `search.py`: A Streamlit app providing simple Q&A via a search bar to query your knowledge base.
- `chat.py`: A Streamlit app providing a simple Chatbot via a search bar to query your knowledge base.

To run either version of the app, please follow the instructions in the respective README.md files in the subdirectories.

## Getting this running...

Install docker, start it, and run `docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest`

### Create `.env` file
- Create a file at the root of the project named `.env`
- Add the following: 
```
OPENAI_API_KEY = "<retrieve value from 1password 'Special Projects or R&D' Vault - Open AI API Token Secure Note>"
NOTION_API_KEY = "<retrieve value from 1password 'Special Projects or R&D' Vault - Notion API Token Secure Note>"
GITHUB_TOKEN = "<set up your own github account using your focusedlabs email, and create a token>"
```