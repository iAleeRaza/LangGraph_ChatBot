import streamlit as st
from chatbot_backend import chatbot_workflow
from langchain_core.messages import HumanMessage


CONFIG = {'configurable' : {'thread_id' : 'thread_1'}}


if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

# loading the conversation history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Type Here...")


if user_input:

    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)
    
    # invoke the chatbot workflow
    response = chatbot_workflow.invoke(
        {'conversation_history':[HumanMessage(content=user_input)]}, 
        config = CONFIG)

    ai_message = response['conversation_history'][-1].content
    st.session_state["message_history"].append({"role": "assistant", "content": ai_message})
    with st.chat_message("assistant"):
        st.text(ai_message)