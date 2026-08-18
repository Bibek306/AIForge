from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage


load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)


class Route(BaseModel):
    next: Literal["rag", "web", "chat", "code"]


supervisor_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a routing supervisor.

Your job is NOT to answer the user's question.
Your only job is to choose the correct agent.

Available agents:

- rag
  Use for questions that require information from the uploaded PDF.

- web
  Use for current information, external information,
  or general knowledge questions.

- code
  Use for programming, coding, debugging,
  algorithms, data structures, and technical questions.

- chat
  Use for greetings, small talk, thanks, goodbye,
  and casual conversation.

Important:

If an agent has already failed to answer the question,
do NOT route the question back to that same agent.

If an agent has already been attempted,
do NOT route the question to that agent again.

Choose the most appropriate remaining agent.

Return only the routing decision.
"""
        ),
        (
            "human",
            """
User question:
{question}

Agent that already failed:
{failed_agent}

Agents already attempted:
{attempted_agents}
"""
        ),
    ]
)


supervisor_chain = (
    supervisor_prompt
    | llm.with_structured_output(Route)
)


def supervisor(state):

    question = next(
        message.content
        for message in reversed(state["messages"])
        if isinstance(message, HumanMessage)
    )

    failed_agent = state.get("failed_agent")

    attempted_agents = state.get(
        "attempted_agents",
        []
    )

    response = supervisor_chain.invoke(
        {
            "question": question,
            "failed_agent": failed_agent or "none",
            "attempted_agents": attempted_agents,
        }
    )

    return {
        "next": response.next,
        "failed_agent": None,
    }