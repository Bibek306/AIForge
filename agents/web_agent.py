from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
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


tavily_tool = TavilySearch(
    max_results=3
)


llm_with_tools = llm.bind_tools(
    [tavily_tool]
)


web_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a web and general-knowledge assistant.

Use your own knowledge when you are confident that
the information is stable and does not require current data.

Use the web search tool when the question requires:

- current or real-time information
- recent events or news
- prices or exchange rates
- weather
- sports results
- information that may have changed recently
- information you are not confident about

After using the web search tool, use the search results
to formulate the final answer.

Do not mention internal tool usage unless the user asks.
"""
        ),
        MessagesPlaceholder("messages"),
    ]
)


web_chain = web_prompt | llm_with_tools


def web_agent(state):

    attempted_agents = state.get(
        "attempted_agents",
        []
    )

    if "web" not in attempted_agents:
        attempted_agents = attempted_agents + ["web"]

    response = web_chain.invoke(
        {
            "messages": state["messages"][-6:]
        }
    )

    return {
        "messages": [
            response
        ],
        "attempted_agents": attempted_agents,
    }