from typing import Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage
import dotenv
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver,sqlite3
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

dotenv.load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)



# for msg_chunk, metadata in  chatbot.stream(
#     {"messages": [HumanMessage(content="Hello!")]},
#     config={"configurable": {"thread_id": "thread-1"}},
#     stream_mode= "messages"
# ):
#     if msg_chunk.content:
#         print(msg_chunk.content, end="", flush=True)

