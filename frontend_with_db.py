import streamlit as st
from backend_with_db import chatbot_workflow, get_all_threads_with_titles
from langchain_core.messages import HumanMessage
import uuid

# ******************************************** Utility Functions *****************************************

# Functions to generate thread IDs, reset chat, add new threads, and load conversations based on thread ID.

def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(st.session_state["thread_id"], title="New Chat")
    st.session_state["message_history"] = []

def add_thread(thread_id, title):

    id_exists = any(chat["id"] == thread_id for chat in st.session_state['chat_threads'])
    
    if not id_exists:
        st.session_state['chat_threads'].append({
            "id": thread_id,
            "title": title
        })

def load_conversation(thread_id):
    return chatbot_workflow.get_state(config = {'configurable' : {'thread_id' : thread_id}}).values['conversation_history']


# ******************************************** Session Setup *****************************************

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    
    st.session_state['chat_threads'] = get_all_threads_with_titles()

add_thread(st.session_state["thread_id"], title="New Chat")

# ******************************************** Sidebar UI *****************************************

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()


st.sidebar.header("My Chats")

for chat in st.session_state['chat_threads']:
    if st.sidebar.button(chat["title"], key=chat["id"]):
        st.session_state["thread_id"] = chat["id"]
        messages = load_conversation(chat["id"])

        temp_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({"role": role, "content": msg.content})
        
        st.session_state['message_history'] = temp_messages

# ******************************************** Main UI *****************************************

for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])


user_input = st.chat_input("Type Here...")

if user_input:
    
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    should_rerun = False
    
    for chat in st.session_state['chat_threads']:
        if chat["id"] == st.session_state["thread_id"] and chat["title"] == "New Chat":
            new_title = user_input[:20] + "..."
            chat["title"] = new_title
            
            from backend_with_db import save_chat_title
            save_chat_title(st.session_state["thread_id"], new_title)
            
            should_rerun = True
    
    for chat in st.session_state['chat_threads']:
        if chat["id"] == st.session_state["thread_id"] and chat["title"] == "New Chat":
            chat["title"] = user_input[:20] + "..."
            should_rerun = True
    
    
    CONFIG = {'configurable' : {'thread_id' : st.session_state["thread_id"]}}
    
    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot_workflow.stream(
                {'conversation_history':[HumanMessage(content=user_input)]}, 
                config = CONFIG,
                stream_mode = 'messages'
            )
        )
    
    st.session_state["message_history"].append({"role": "assistant", "content": ai_message})

    if should_rerun:
        st.rerun()