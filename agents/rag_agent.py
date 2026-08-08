import os
import tempfile
import hashlib
import streamlit as st

from dotenv import load_dotenv

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains import (
    create_retrieval_chain,
    create_history_aware_retriever,
)
from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain,
)

from langchain_core.messages import AIMessage

load_dotenv()


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def initialize_rag(uploaded_file, thread_id):

    if "rag_chains" not in st.session_state:
        st.session_state.rag_chains = {}

    file_bytes = uploaded_file.getvalue()

    file_hash = hashlib.md5(file_bytes).hexdigest()

    existing = st.session_state.rag_chains.get(thread_id)

    if existing and existing["file_hash"] == file_hash:
        return

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:

        temp_file.write(file_bytes)
        temp_path = temp_file.name

    file_extension = os.path.splitext(uploaded_file.name)[1].lower()

    if file_extension == ".pdf":
        loader = PyPDFLoader(temp_path)

    elif file_extension == ".docx":
        loader = Docx2txtLoader(temp_path)

    elif file_extension == ".txt":
        loader = TextLoader(
            temp_path,
            encoding="utf-8"
        )

    else:
        raise ValueError(
            f"Unsupported file type: {file_extension}"
        )

    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    splits = text_splitter.split_documents(documents)
    if not splits:
        st.error("Could not extract text from this PDF.")
        return

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    contextualize_q_system_prompt = (
        "Given the chat history and the latest user question, "
        "rewrite the latest question into a standalone question "
        "that can be understood without the chat history. "
        "Do NOT answer the question. "
        "Only rewrite it if needed."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("messages"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm=llm,
        retriever=retriever,
        prompt=contextualize_q_prompt,
    )

    system_prompt = (
        "You are a document question-answering assistant. "
        "Answer the user's question using ONLY the provided context "
        "from the uploaded document. "
        "Do not use your own general knowledge to fill in missing information. "
        "If the answer cannot be found in the provided context, "
        "say exactly: "
        "'I don't know based on the provided documents.'\n\n"
        "Context:\n{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("messages"),
            ("human", "{input}"),
        ]
    )

    document_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=qa_prompt,
    )

    retrieval_chain = create_retrieval_chain(
        history_aware_retriever,
        document_chain,
    )

    st.session_state.rag_chains[thread_id] = {
        "chain": retrieval_chain,
        "file_hash": file_hash,
        "file_name": uploaded_file.name,
    }

    os.remove(temp_path)


def rag_agent(state, config):

    thread_id = config["configurable"]["thread_id"]

    rag_data = st.session_state.get(
        "rag_chains",
        {}
    ).get(thread_id)

    attempted_agents = state.get(
        "attempted_agents",
        []
    )

    if "rag" not in attempted_agents:
        attempted_agents = attempted_agents + ["rag"]

    if rag_data is None:

        return {
            "messages": [
                AIMessage(
                    content="Please upload a PDF before asking a document-related question."
                )
            ],
            "next": "end",
            "failed_agent": None,
            "attempted_agents": attempted_agents,
        }

    retrieval_chain = rag_data["chain"]

    result = retrieval_chain.invoke(
        {
            "input": state["messages"][-1].content,
            "messages": state["messages"][-7:-1],
        }
    )

    answer = result["answer"]

    if answer == "I don't know based on the provided documents.":

        return {
            "messages": [
                AIMessage(content=answer)
            ],
            "next": "supervisor",
            "failed_agent": "rag",
            "attempted_agents": attempted_agents,
        }

    return {
        "messages": [
            AIMessage(content=answer)
        ],
        "next": "end",
        "failed_agent": None,
        "attempted_agents": attempted_agents,
    }