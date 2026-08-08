from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

from state import GraphState

from agents.supervisor import supervisor
from agents.rag_agent import rag_agent
from agents.web_agent import web_agent, tavily_tool
from agents.chat_agent import chat_agent
from agents.code_agent import code_agent


builder = StateGraph(GraphState)


# TOOLS

tool_node = ToolNode(
    [tavily_tool]
)


# NODES

builder.add_node(
    "supervisor",
    supervisor
)

builder.add_node(
    "rag",
    rag_agent
)

builder.add_node(
    "web",
    web_agent
)

builder.add_node(
    "chat",
    chat_agent
)

builder.add_node(
    "code",
    code_agent
)

builder.add_node(
    "tools",
    tool_node
)


# START

builder.add_edge(
    START,
    "supervisor"
)


# SUPERVISOR ROUTING

def route_supervisor(state):
    return state["next"]


builder.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "rag": "rag",
        "web": "web",
        "chat": "chat",
        "code": "code",
    },
)


# RAG ROUTING

def route_rag(state):
    return state["next"]


builder.add_conditional_edges(
    "rag",
    route_rag,
    {
        "supervisor": "supervisor",
        "end": END,
    },
)


# CHAT

builder.add_edge(
    "chat",
    END
)


# CODE

builder.add_edge(
    "code",
    END
)


# WEB + TOOLS

builder.add_conditional_edges(
    "web",
    tools_condition,
)


builder.add_edge(
    "tools",
    "web"
)


# MEMORY

memory = MemorySaver()


graph = builder.compile(
    checkpointer=memory
)