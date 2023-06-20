import os
from llama_hub.github_repo import GithubRepositoryReader, GithubClient
from llama_index import LLMPredictor, VectorStoreIndex, ServiceContext
from langchain import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 0. Make sure GITHUB_TOKEN and OPENAI_API_KEY are in the environment (or in the run config if running in PyCharm)
github_client = GithubClient(os.getenv("GITHUB_TOKEN"))

# 1. Load documents
loader = GithubRepositoryReader(
    github_client,
    owner="awesomekling",
    repo="serenity",
    filter_file_extensions=([".cpp", ".md", ".txt"], GithubRepositoryReader.FilterType.INCLUDE),
    verbose=False,
)

docs = loader.load_data(branch="master")

# 2. Build an index
llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-davinci-003"))
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
index = VectorStoreIndex.from_documents(
    docs, service_context=service_context
)

# 3. Store the index
index.storage_context.persist(persist_dir="github_repos/serenityos/index")
