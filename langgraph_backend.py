from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
load_dotenv()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm =ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_retries=2)

def chat_node(state: ChatState):

    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages': [response]}

graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

checkpointer= MemorySaver()

chatbot = graph.compile(checkpointer=checkpointer)
chatbot