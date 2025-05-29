import os
from dotenv import load_dotenv, dotenv_values
from openai import OpenAI
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3.1:8b")

llm.invoke("The first man on the moon was ...")

# # loading variables from .env file
# load_dotenv()
# client = OpenAI()
# 
# prompt = """
# List the top 30 unique, common terms and keywords typically found in an invoice document, lowercase, no stopwords.
# """
# 
# response = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[{"role": "user", "content": prompt}],
# )
# 
# keywords = response.choices[0].message.content
# print(keywords)
# 