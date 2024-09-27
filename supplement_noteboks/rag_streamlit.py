# สร้าง retriever
import streamlit as st
import chromadb
import os
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.retrievers import BaseRetriever
from llama_index.core import PromptTemplate
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.file.docs import PDFReader

import chromadb.api

chromadb.api.client.SharedSystemClient.clear_system_cache()

os.environ["OPENAI_API_KEY"] = "..." # ใส่ OpenAI API key ที่นี้
PDF_DATA_PATH="assets/personal_data_protection_policy.pdf"
CHUNK_SIZE=1000
CHUNK_OVERLAP=250
OPENAI_TEMP=0
CHROMA_PERSISTENCE_PATH="./chroma_db"
CHROMA_COLLECTION_NAME="test4543ss332"
RETRIEVER_TOP_K=5
QUERY_PROMPT_TEMPLATE = """
# Task
From given document answer the following question.

# Instructions
- Answer the following question based on the given document and chat history.
- You need to cite the source of the answer from the document.

# Document:
{document}

---
# Chat History:
{chat_history}
---
# Question:
{question}

# Answer:
"""

reader = PDFReader()
embedder = OpenAIEmbedding(model="text-embedding-3-large")
text_splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
splitter = TokenTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)


def generate_retriever(documents) -> VectorStoreIndex:
    db = chromadb.Client()
    
    # [OPTIONAL] delete if existing
    try:
        db.delete_collection(CHROMA_COLLECTION_NAME)
    except ValueError:
        print("[ChromaDB] Failed to delete collection.")
        
    chroma_collection = db.create_collection(CHROMA_COLLECTION_NAME)
    
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # StorageContext is not ded like the other one
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    nodes = splitter.get_nodes_from_documents(documents)
    
    index = VectorStoreIndex(nodes, storage_context=storage_context, show_progress=True)
    return index


def get_answer_from_rag(
    retriever: BaseRetriever,
    llm: OpenAI,
    qa_prompt: PromptTemplate,
    question: str,
    chat_history: str = "",
) -> str:
    # Retrieve the chunks
    chunks = retriever.retrieve(question)
    response = llm.complete(
        qa_prompt.format(
            document=chunks,
            question=question,
            chat_history=chat_history,
        )
    )
    
    return response


### Start the pipeline
Settings.node_parser = splitter
Settings.embed_model = embedder
Settings.chunk_size=CHUNK_SIZE
Settings.chunk_overlap=CHUNK_OVERLAP
Settings.llm = OpenAI(model="gpt-4o")

documents = reader.load_data(PDF_DATA_PATH)
vector_store_index = generate_retriever(documents)
retriever = vector_store_index.as_retriever(similarity_top_k=RETRIEVER_TOP_K)
query_engine = vector_store_index.as_query_engine()


### Streamlit app
st.set_page_config(page_title="Chatbot", page_icon="", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title('Chat Interface')

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "สอบถามข้อมูลที่สนใจ"}
    ]

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
messages = getattr(st.session_state, 'messages', [])
for message in messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])


#If last message is not from assistant, generate a new response
if messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_answer_from_rag(
                retriever=query_engine,
                llm=Settings.llm,
                qa_prompt=QUERY_PROMPT_TEMPLATE,
                question=prompt,
                chat_history=str(st.session_state.messages)
            )
            response = response.text
            st.write(response)
            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message) # Add response to message history