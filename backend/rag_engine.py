import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Directory to persist vector database
DB_DIR = "db"

# Prompt template to guide the model
prompt_template = """
You are a helpful assistant. The following is a transcript of a YouTube video. 
Answer the user's question based on the content of the video.

Transcript:
{context}

Question: {question}
Answer:
"""

# LangChain PromptTemplate object
QA_PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# Embedding and LLM initialization
embedding = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

def ingest_transcript(transcript_chunks):
    """Process and store transcript chunks into Chroma vector DB."""
    docs = []

    # Context to help with summary-style questions
    docs.append(Document(
        page_content="This is a transcript of a YouTube video. It may contain narration, interviews, or lyrics.",
        metadata={"type": "context"}
    ))

    # Timestamped segments
    for chunk in transcript_chunks:
        text = chunk.get("text", "")
        if text:
            metadata = {"start_time": chunk.get("start_time", "00:00")}
            docs.append(Document(page_content=text, metadata=metadata))

    # Add full transcript as one doc for broader context
    full_text = " ".join(chunk.get("text", "") for chunk in transcript_chunks)
    if full_text.strip():
        docs.append(Document(page_content=full_text, metadata={"type": "full"}))

    if not docs:
        raise ValueError("No valid transcript data found to ingest.")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=50,
        separators=["\n", ".", "!", "?", ",", " "]
    )
    split_docs = splitter.split_documents(docs)

    # Save to Chroma DB
    vector_db = Chroma.from_documents(split_docs, embedding, persist_directory=DB_DIR)
    print(f"✅ Ingested {len(split_docs)} transcript chunks into the vector DB.")


def get_answer(question):
    """Retrieve an answer using the vector DB and custom prompt."""
    try:
        vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embedding)
    except Exception as e:
        print("❌ Failed to load vector DB:", e)
        return {"result": "Error accessing the vector database."}

    retriever = vector_db.as_retriever()
    retriever.search_kwargs["k"] = 5  # Retrieve top-5 chunks

    # Define the QA chain using the custom prompt
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # Stuff all context together
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_PROMPT}
    )

    try:
        result = qa_chain.invoke({"query": question})
        print("\n🎯 Question:", question)
        print("💬 Answer:", result['result'])
        print("📄 Retrieved Chunks:")
        for doc in result['source_documents']:
            print("→", doc.page_content[:200], "\n")

        return result
    except Exception as e:
        print("❌ Error during QA:", e)
        return {"result": "Error during QA."}
