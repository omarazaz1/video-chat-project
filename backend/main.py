from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from video_utils import get_youtube_transcript
from rag_engine import ingest_transcript, get_answer
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class VideoRequest(BaseModel):
    url: str

class QuestionRequest(BaseModel):
    question: str

# Routes
@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.post("/transcript")
async def transcript(req: VideoRequest):
    result = get_youtube_transcript(req.url)
    return {"transcript": result}

@app.post("/ingest")
def ingest_route(data: VideoRequest):
    chunks = get_youtube_transcript(data.url)
    ingest_transcript(chunks)
    return {"message": "Transcript ingested", "chunks": chunks}

@app.post("/ask")
def ask_question_route(q: QuestionRequest):
    answer = get_answer(q.question)
    return {"answer": answer}
