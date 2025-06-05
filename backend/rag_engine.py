import os
from langchain_community.document_loaders import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.schema import Document as LangchainDoc

# Initialize LLM and Embeddings
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
embedding = OpenAIEmbeddings()

# Global DB for now (will store transcripts here)
vector_db = None

def ingest_transcript(transcript_chunks):
    global vector_db
    # Convert transcript to Langchain-compatible documents
    docs = [LangchainDoc(page_content=chunk["text"], metadata={"link": chunk["link"]}) for chunk in transcript_chunks]

    # Split into smaller chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    # Embed and store in Chroma
    vector_db = Chroma.from_documents(split_docs, embedding)

def get_answer(question):
    if not vector_db:
        return "No transcript data available yet."
    
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_db.as_retriever()
    )
    result = qa.run(question)
    return result
