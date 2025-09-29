from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama   
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
import requests

# -------------------
# 1. LLM (Ollama)
# -------------------

llm = ChatOllama(
    model="llama3.2:1b",  # <-- or "llama3", or any valid name from `ollama list`
    base_url="http://localhost:11434"
)
# -------------------
# 2. Tools
# -------------------
@tool
def calculator(a: float, b: float, operation: str) -> dict:
    """A simple calculator tool that can add or multiply two numbers."""
    if operation == "add":
        return {"result": a + b}
    elif operation == "mul":
        return {"result": a * b}
    return {"error": "Unsupported operation"}

@tool
def get_weather(city: str) -> dict:
    """Get the current weather for a given city using wttr.in API."""
    r = requests.get(f"https://wttr.in/{city}?format=j1")
    data = r.json()
    return {"city": city, "temp": data["current_condition"][0]["temp_C"]}



tools = [calculator, get_weather]

# -------------------
# 3. State
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Nodes
# -------------------
def chat_node(state: ChatState):
    """LLM node"""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools)

# -------------------
# 5. Graph
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", tools_condition)
graph.add_edge("tools", "chat")
graph.add_edge("chat", END)

chatbot = graph.compile()

# -------------------
# 6. Run
# -------------------
user_input = HumanMessage(content="What’s the weather in London? Also multiply 5 * 7")
result = chatbot.invoke({"messages": [user_input]})
print(result["messages"][-1].content)
