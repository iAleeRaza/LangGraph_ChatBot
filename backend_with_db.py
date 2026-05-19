from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

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
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)  # This will create the database file if it doesn't exist
def create_title_table():
    with sqlite3.connect('chatbot.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS chat_titles (thread_id TEXT PRIMARY KEY, title TEXT)")

create_title_table()

def save_chat_title(thread_id, title):
    with sqlite3.connect('chatbot.db') as conn:
        conn.execute("INSERT OR REPLACE INTO chat_titles (thread_id, title) VALUES (?, ?)", (thread_id, title))
checkpointer = SqliteSaver(conn=conn)

# nodes
graph.add_node('chat_node', chat_node)

#edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# compiling the graph into a workflow
chatbot_workflow = graph.compile(checkpointer=checkpointer)

def get_all_threads_with_titles():
    with sqlite3.connect('chatbot.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT thread_id, title FROM chat_titles")
        results = cursor.fetchall()
        return [{"id": row[0], "title": row[1]} for row in results]