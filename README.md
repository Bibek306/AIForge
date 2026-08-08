# AIForge — Multi-Agent AI Assistant

AIForge is a multi-agent AI assistant built using **LangGraph, LangChain, Groq, Ollama, Chroma, Tavily, and Streamlit**.

It uses a **Supervisor Agent** to route user queries to specialized agents.

## Features

- 🤖 Supervisor-based agent routing
- 📄 PDF,txt,docx upload and RAG-based Q&A
- 🌐 Web search using Tavily
- 💻 Code Agent for programming questions
- 💬 Chat Agent for general conversation
- 🔄 Agent fallback mechanism
- 🧠 Conversation memory with LangGraph
- 🛠️ Tool calling with `tools_condition`

## Architecture

                           User
                            │
                 ┌──────────┴──────────┐
                 │                     │
             Question              File Upload
                 │                     │
                 │                     ▼
                 │                RAG Pipeline
                 │                     │
                 └──────────┬──────────┘
                            ▼
                       Supervisor
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
        RAG                Web               Code
          │                 │                 │
          │                 ▼                 │
          │              Tavily              │
          │                 │                 │
          │                 ▼                 │
          │              ToolNode             │
          │                 │                 │
          └───────┐         │                 │
                  │         │                 │
                  ▼         ▼                 ▼
               Answer    Web Answer       Code Answer
                  │         │                 │
                  └─────────┼─────────────────┘
                            │
                            ▼
                           Chat
                            │
                            ▼
                         Response

RAG unable to answer
          │
          ▼
      Supervisor
          │
          ▼
   Web / Code / Chat


## Tech Stack

Python
Streamlit
LangGraph
LangChain
Groq
Ollama
Chroma
Tavily

# Models
Component	   Model
Supervisor  llama-3.3-70b-versatile
RAG	        llama-3.3-70b-versatile
Web	        llama-3.1-8b-instant
Code	      llama-3.1-8b-instant
Chat	      llama-3.1-8b-instant
Embeddings	nomic-embed-text

# Project Structure

AIForge/
│
├── app.py
├── graph.py
├── state.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── agents/
    ├── supervisor.py
    ├── rag_agent.py
    ├── web_agent.py
    ├── chat_agent.py
    └── code_agent.py

# Run Locally

git clone <your-repository-url>
cd AIForge

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
ollama pull nomic-embed-text

streamlit run app.py