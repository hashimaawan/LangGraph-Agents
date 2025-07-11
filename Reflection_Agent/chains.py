import os 
from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


llm = init_chat_model("google_genai:gemini-1.5-flash", temperature=0.3, google_api_key=GOOGLE_API_KEY)

initial_chain = PromptTemplate.from_template("""
You are a reasoning agent. Given a question, respond with a thoughtful answer.
Question: {question}
Answer:""") | llm

reflection_chain = PromptTemplate.from_template("""
You are a reflection agent. Critically analyze the following answer and suggest improvements.

Question: {question}
Initial Answer: {initial_answer}
Reflection:""") | llm

improvement_chain = PromptTemplate.from_template("""
Use the reflection below to improve the original answer.

Question: {question}
Initial Answer: {initial_answer}
Reflection: {reflection}
Improved Answer:""") | llm