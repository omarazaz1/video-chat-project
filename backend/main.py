# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from video_utils import get_youtube_transcript
# from rag_engine import ingest_transcript, get_answer
# from dotenv import load_dotenv

# load_dotenv()
# from langchain_openai import ChatOpenAI
# # Initialize FastAPI app
# app = FastAPI()

# # CORS setup
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Request models
# class VideoRequest(BaseModel):
#     url: str

# class QuestionRequest(BaseModel):
#     question: str

# # Routes
# @app.get("/")
# def root():
#     return {"message": "Backend is running"}

# @app.post("/transcript")
# async def transcript(req: VideoRequest):
#     result = get_youtube_transcript(req.url)
#     return {"transcript": result}

# @app.post("/ingest")
# def ingest_route(data: VideoRequest):
#     result = get_youtube_transcript(data.url)
#     transcript = result.get("transcript", result)  # Support both dict or direct list

#     if not isinstance(transcript, list):
#         return {"error": "Transcript not found or invalid format."}

#     ingest_transcript(transcript)
#     return {"message": "Transcript ingested", "chunks": transcript}


# @app.post("/ask")
# def ask_question_route(q: QuestionRequest):
#     answer = get_answer(q.question)
#     return {"answer": answer}

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from video_utils import get_youtube_transcript
from rag_engine import ingest_transcript, get_answer
from dotenv import load_dotenv
import os

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Pydantic request models
class VideoRequest(BaseModel):
    url: str

class QuestionRequest(BaseModel):
    question: str

# ✅ Health check route
@app.get("/")
def root():
    return {"message": "Backend is running"}

# ✅ Route to get transcript chunks from a YouTube URL
@app.post("/transcript")
async def transcript_route(req: VideoRequest):
    try:
        result = get_youtube_transcript(req.url)
        return {"transcript": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Route to ingest transcript into Chroma vector store
@app.post("/ingest")
def ingest_route(req: VideoRequest):
    result = get_youtube_transcript(req.url)

    # Handle both list or dict formats
    if isinstance(result, list):
        transcript = result
    elif isinstance(result, dict) and "transcript" in result:
        transcript = result["transcript"]
    else:
        raise HTTPException(status_code=400, detail="Transcript not found or invalid format.")

    ingest_transcript(transcript)
    return {"message": "Transcript ingested and vector DB built!"}

# ✅ Route to answer questions using the ingested transcript
@app.post("/ask")
def ask_route(q: QuestionRequest):
    try:
        answer = get_answer(q.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
