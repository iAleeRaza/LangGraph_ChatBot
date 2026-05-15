from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

# loading API key
load_dotenv()

#__________________
# LLM 
#__________________
llm = ChatGroq(model='llama-3.1-8b-instant')

# State class
class ChatState(TypedDict):

    conversation_history: Annotated[list[BaseMessage], add_messages]


# function for chat_node
def chat_node(state: ChatState):

    # take the user query from the conversation history
    messages = state['conversation_history']

    # generate a response using the language model
    response = llm.invoke(messages)
    # add the response to the conversation history
    return {'conversation_history': [response]}


# graph definition
graph = StateGraph(ChatState)

# checkpointer to save the graph state in memory
checkpointer = MemorySaver()

# nodes
graph.add_node('chat_node', chat_node)

#edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# compiling the graph into a workflow
chatbot_workflow = graph.compile(checkpointer=checkpointer)


