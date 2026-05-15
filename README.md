## 🧠 Learning LangGraph: Building a Context-Aware Chatbot

This repository serves as a hands-on project built to explore and learn the core concepts of **State Management**, **Short-Term Memory**, and **Session Checkpointting** in LLM applications. 

By integrating **LangGraph**, **LangChain**, and **Streamlit**, the primary goal of this project was to understand how production-grade, fault-tolerant AI agents manage conversation history and maintain state across user interactions.

---

### 📚 Concepts Explored & Learned

Through the development of this learning project, I gained practical experience with the following advanced AI engineering concepts:

1. **Stateful Graph Orchestration**
   * Learned how to use LangGraph's `StateGraph` to define functional blocks as **Nodes** and control the workflow execution using **Edges** (from `START` to `END`).

2. **Short-Term Memory & Checkpointing**
   * Explored how `MemorySaver` works as a checkpointer layer.
   * Learned how thread-based persistence (`thread_id`) allows the graph to capture state snapshots at every step, enabling a chatbot to remember context across conversations or resume seamlessly after a system crash.

3. **State Updates via Message Accumulators**
   * Understood the use of `Annotated` schemas combined with `add_messages` to cleanly append new interactions into the conversation history rather than manually managing list updates or overwriting states.

4. **Streamlit Session State Integration**
   * Learned how to connect a stateful backend graph with Streamlit's frontend `session_state` to render a clean, real-time UI chat interface.

---

### 🛠️ Tech Stack Used

* **Orchestration Framework:** [LangGraph](https://github.com/langchain-ai/langgraph) (For building the state machine and handling persistence)
* **LLM Wrapper:** [LangChain Core](https://github.com/langchain-ai/langchain) (For structure-based message objects like `HumanMessage`, `AIMessage`)
* **Inference Engine:** [Groq Cloud API](https://groq.com/) (For high-speed LLM processing)
* **UI Interface:** [Streamlit](https://streamlit.io/) (For local testing and deployment)
