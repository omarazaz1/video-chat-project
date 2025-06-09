
import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

# ✅ LangChain and related imports
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.schema import Document as LangchainDoc

# ✅ Directory to persist the vector database
DB_DIR = "db"

# ✅ Initialize embeddings and LLM with API key
embedding = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))



def ingest_transcript(transcript_chunks):
    # ✅ Convert transcript chunks into LangChain documents
    docs = []
    for chunk in transcript_chunks:
        text = chunk.get("text", "")
        metadata = {"start": chunk.get("start", 0.0)}
        if text:
            docs.append(Document(page_content=text, metadata=metadata))

    if not docs:
        raise ValueError("No valid transcript chunks provided")

    # ✅ Split long docs into smaller chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    # ✅ Create or update persistent vector DB
    vector_db = Chroma.from_documents(split_docs, embedding, persist_directory=DB_DIR)
   # vector_db.persist()
    print(f"✅ Ingested {len(split_docs)} chunks into vector DB.")


# ✅ Get answer from vector DB using LLM
def get_answer(question):
    # Reload the persistent vector DB
    vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embedding)

    try:
        docs = vector_db.get()["documents"]
        print(f"✅ Loaded {len(docs)} documents from vector DB.")
    except Exception as e:
        print(" Failed to load vector DB:", e)
        return "Error accessing the vector database."

    # Run RetrievalQA
    retriever = vector_db.as_retriever()
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    #result = qa.run(question)
    result = qa.invoke({"query": question})

    return result
