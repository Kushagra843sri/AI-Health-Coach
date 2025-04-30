from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
import os

def initialize_rag():
    # Load health tips from file
    with open("data/health_tips.txt", "r") as file:
        health_tips = file.read()
    
    # Split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = text_splitter.split_text(health_tips)
    
    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vector_store = FAISS.from_texts(documents, embeddings)
    
    # Initialize LLM
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    # Create RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever()
    )
    return qa_chain

def get_health_tip(query: str, qa_chain):
    return qa_chain.run(query)