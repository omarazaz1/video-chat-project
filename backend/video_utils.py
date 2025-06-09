### video_utils.py
from youtube_transcript_api import YouTubeTranscriptApi
import urllib.parse

def extract_video_id(url: str) -> str:
    parsed_url = urllib.parse.urlparse(url)
    if "youtube.com" in parsed_url.netloc:
        query = urllib.parse.parse_qs(parsed_url.query)
        return query.get("v", [None])[0]
    elif "youtu.be" in parsed_url.netloc:
        return parsed_url.path.strip("/")
    return None

def format_time(seconds: float) -> str:
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes:02}:{seconds:02}"

def get_youtube_transcript(url: str):
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return {"error": "Could not extract video ID from URL."}

        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])

        chunk_size = 30
        chunks = []
        chunk_text = ""
        chunk_start = transcript[0]['start']
        current_time = chunk_start

        for entry in transcript:
            if entry['start'] < current_time + chunk_size:
                chunk_text += " " + entry['text']
            else:
             
                chunks.append({
    "start_time": format_time(chunk_start),
    "link": f"https://www.youtube.com/watch?v={video_id}&t={int(chunk_start)}s",
    "text": chunk_text.strip()
})
                chunk_text = entry['text']
                chunk_start = entry['start']
                current_time = chunk_start

        if chunk_text:
            chunks.append({
                "timestamp": format_time(chunk_start),
                "text": chunk_text.strip()
            })

        return chunks
    except Exception as e:
        return {"error": f"Error fetching transcript: {str(e)}"}
