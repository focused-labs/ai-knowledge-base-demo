import time
from llama_index import StorageContext, load_index_from_storage

storage_context = StorageContext.from_defaults(persist_dir="github_repos/serenityos/index")

index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine()

# role = "UX designer"
# role_description = "a person who is responsible for the user experience of a product"

# role = "UI designer"
# role_description = "a person who is responsible for the look and feel of a product"

role = "software engineer"
role_description = "a person who writes code for a product"

# role = "expert C++ programmer"
# role_description = "a person who writes C++ code for a product"

# role = "stakeholder"
# role_description = "a person who has a financial or intellectual interest in a project"

# What are the user-visible components in the SerenityOS software?

# What are the most important features of the SerenityOS software?
# Rank them in an ordered list where 1 is most important.

# Consider only the C++ code in SerenityOS. What are the most important C++ classes?
# Rank them in an ordered list where 1 is most important.

# How does Serenity OS implement pre-emptive multi-threading?

# What video codecs does SerenityOS use?

# What graphics library do SerenityOS applications use?

# Show me some C++ code from Serenity OS that uses the VP9 video codec.

start_time = time.time()

query = f"""
A {role} is {role_description}. 
Your role on SerenityOS is {role}.
What is the purpose of the AudioServer?
"""
print(query)
response = query_engine.query(query)
print(response)

elapsed_time = round(time.time() - start_time, 2)
print(f"\nElapsed time in sec: {elapsed_time}")

