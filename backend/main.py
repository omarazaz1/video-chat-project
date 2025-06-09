
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from video_utils import get_youtube_transcript
from rag_engine import ingest_transcript, get_answer
from fastapi import Request #
from dotenv import load_dotenv
import os

#  Load environment variables from .env
load_dotenv()

#  Initialize FastAPI app
app = FastAPI()

#  Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Pydantic request models
class VideoRequest(BaseModel):
    url: str

class QuestionRequest(BaseModel):
    question: str

#  Health check route
@app.get("/")
def root():
    return {"message": "Backend is running"}

# Route to get transcript chunks from a YouTube URL
@app.post("/transcript")
async def transcript_route(req: VideoRequest):
    try:
        result = get_youtube_transcript(req.url)
        return {"transcript": result}
    except Exception as e:
        print(f"❌ Error in /transcript: {e}")
        return {"transcript": {"error": f"Error fetching transcript: {str(e)}"}}


@app.post("/ingest")
async def ingest_route(req: Request):
    body = await req.json()
    print(" Incoming ingest body:", body)

    transcript = body.get("transcript")
    if not isinstance(transcript, list):
        raise HTTPException(status_code=400, detail="Transcript must be a list.")

    ingest_transcript(transcript)
    return {"message": "Transcript ingested!"}

#  Route to answer questions using the ingested transcript
@app.post("/ask")
def ask_route(q: QuestionRequest):
    try:
        answer = get_answer(q.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
