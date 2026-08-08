import streamlit as st

from graph import graph
from agents.rag_agent import initialize_rag

from langchain_core.messages import HumanMessage, AIMessage


st.title("AI-Forge")


# GRAPH CONFIG

config = {
    "configurable": {
        "thread_id": "user_1"
    }
}


# CHAT HISTORY

state = graph.get_state(config)

messages = state.values.get(
    "messages",
    []
)

for message in messages:

    if isinstance(message, HumanMessage):

        st.chat_message("user").write(
            message.content
        )

    elif isinstance(message, AIMessage):

        st.chat_message("assistant").write(
            message.content
        )


# CHAT INPUT + PDF UPLOAD

prompt = st.chat_input(
    "Ask something...",
    accept_file=True,
    file_type=["pdf","docx","txt"]
)


if prompt:

    user_input = prompt.text
    files = prompt.files


    # PDF UPLOAD

    if files:

        initialize_rag(
            files[0],
            config["configurable"]["thread_id"]
        )

        st.chat_message("user").write(
            f"📎 {files[0].name}"
        )


    # USER QUESTION

    if user_input:

        st.chat_message("user").write(
            user_input
        )

        graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=user_input
                    )
                ],

                # Reset for every new question
                "attempted_agents": [],

                "failed_agent": None,
            },
            config=config
        )


    st.rerun()