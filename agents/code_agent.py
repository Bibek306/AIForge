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


code_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert programming assistant.

Help the user with:

- programming
- coding
- debugging
- algorithms
- data structures
- technical implementation

Provide correct and clear code when code is requested.

If the user provides code, analyze it carefully and
preserve their intended approach unless a better approach
is explicitly requested.

Do not mention internal agents or routing.
"""
        ),
        MessagesPlaceholder("messages"),
    ]
)


code_chain = code_prompt | llm


def code_agent(state):

    attempted_agents = state.get(
        "attempted_agents",
        []
    )

    if "code" not in attempted_agents:
        attempted_agents = attempted_agents + ["code"]

    response = code_chain.invoke(
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