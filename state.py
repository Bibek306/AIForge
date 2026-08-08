from typing import Literal
from langgraph.graph import MessagesState
from pydantic import Field


class GraphState(MessagesState):
    next: Literal[
        "rag",
        "web",
        "chat",
        "code",
        "supervisor",
        "end"
    ]

    failed_agent: Literal[
        "rag",
        "web",
        "chat",
        "code"
    ] | None = None

    attempted_agents: list[str] = Field(
        default_factory=list
    )