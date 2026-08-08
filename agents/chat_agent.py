from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import AIMessage


load_dotenv()


llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
)


chat_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a friendly AI assistant.

Answer conversational questions naturally.

Do not search the web.

Do not mention PDFs unless the user asks.
"""
        ),
        MessagesPlaceholder("messages"),
    ]
)


chat_chain = chat_prompt | llm


def chat_agent(state):

    attempted_agents = state.get(
        "attempted_agents",
        []
    )

    if "chat" not in attempted_agents:
        attempted_agents = attempted_agents + ["chat"]

    response = chat_chain.invoke(
        {
            "messages": state["messages"][-6:]
        }
    )

    return {
        "messages": [
            AIMessage(content=response.content)
        ],
        "next": "end",
        "failed_agent": None,
        "attempted_agents": attempted_agents,
    }