from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from video_utils import get_youtube_transcript
from rag_engine import ingest_transcript, get_answer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend access
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

# Health check
@app.get("/")
def root():
    return {"message": "✅ Backend is running"}

# Endpoint: Fetch transcript
@app.post("/transcript")
async def transcript_route(req: VideoRequest):
    try:
        result = get_youtube_transcript(req.url)
        return {"transcript": result}
    except Exception as e:
        print(f"❌ Error in /transcript:", e)
        return {"transcript": {"error": f"Error fetching transcript: {str(e)}"}}

# Endpoint: Ingest transcript
@app.post("/ingest")
async def ingest_route(req: Request):
    try:
        body = await req.json()
        transcript = body.get("transcript")
        if not isinstance(transcript, list):
            raise HTTPException(status_code=400, detail="Transcript must be a list.")
        ingest_transcript(transcript)
        return {"message": "✅ Transcript ingested!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingest error: {str(e)}")

# Endpoint: Ask question
@app.post("/ask")
def ask_route(q: QuestionRequest):
    try:
        answer = get_answer(q.question)  # This must use the custom prompt in rag_engine.py
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answering error: {str(e)}")
