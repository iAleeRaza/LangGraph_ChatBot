from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import requests

# loading API key
load_dotenv()

#__________________
#1. LLM 
#__________________
llm = ChatGroq(model='llama-3.1-8b-instant')


# -------------------
# 2. Tools
# -------------------
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=O8RCXRB77KOA0ZD8"
    r = requests.get(url)
    return r.json()



tools = [search_tool, get_stock_price, calculator]
llm_with_tools = llm.bind_tools(tools)


# -------------------
# 3. State
# -------------------
class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]


# -------------------
# 4. ChatNode
# -------------------
def chat_node(state: ChatState):

    # take the user query from the conversation history
    messages = state['messages']

    # generate a response using the language model
    response = llm_with_tools.invoke(messages)
    # add the response to the conversation history
    return {'messages': [response]}

tool_node = ToolNode(tools)


# -------------------
# 5. Database and Checkpointer
# -------------------
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)  # This will create the database file if it doesn't exist
def create_title_table():
    with sqlite3.connect('chatbot.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS chat_titles (thread_id TEXT PRIMARY KEY, title TEXT)")

create_title_table()

def save_chat_title(thread_id, title):
    with sqlite3.connect('chatbot.db') as conn:
        conn.execute("INSERT OR REPLACE INTO chat_titles (thread_id, title) VALUES (?, ?)", (thread_id, title))
checkpointer = SqliteSaver(conn=conn)

# -------------------
# 6. Graph
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node')

# compiling the graph into a workflow
chatbot_workflow = graph.compile(checkpointer=checkpointer)

def get_all_threads_with_titles():
    with sqlite3.connect('chatbot.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT thread_id, title FROM chat_titles")
        results = cursor.fetchall()
        return [{"id": row[0], "title": row[1]} for row in results]