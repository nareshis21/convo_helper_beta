from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import os
import time
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
# llm_instance = ChatOpenAI(
#     openai_api_base="https://api.groq.com/openai/v1",
#     openai_api_key=api_key,
#     model_name="llama-3.1-8b-instant",
#     temperature=0.7
# )

# start_time=time.time()
# t=llm_instance.invoke("Hi")
# end_time = time.time()
# print(t.content)
# print("Execution Time:", end_time - start_time, "seconds")

llm_g =ChatGroq(api_key=api_key,
              model="llama-3.1-8b-instant",
              max_retries=2,timeout=None,
              max_tokens=2000,
              temperature=0.7)

# start_time=time.time()
# t=llm.invoke("Hi")
# end_time = time.time()
# print(t.content)
# print("Execution Time:", end_time - start_time, "seconds")