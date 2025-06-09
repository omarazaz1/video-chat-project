
import urllib.parse
import subprocess
import json
import os

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
        print(" Extracted video ID:", video_id)
        if not video_id:
            return {"error": "Could not extract video ID from URL."}

        # Use yt-dlp to get subtitles in JSON
        result = subprocess.run(
            [
                "yt-dlp",
                "--write-auto-sub",
                "--sub-format", "json3",
                "--skip-download",
                "-o", "%(id)s.%(ext)s",
                url
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        json_file = f"{video_id}.live_chat.json"  # fallback if JSON is not found
        for ext in ['en.json3', 'en-US.json3', 'en.vtt.json', 'en.vtt']:
            if os.path.exists(f"{video_id}.{ext}"):
                json_file = f"{video_id}.{ext}"
                break

        if not os.path.exists(json_file):
            return {"error": "Transcript file not found after yt-dlp run."}

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Example parse: extract text and timestamps (you may need to adjust)
        events = data.get("events", [])
        transcript = []
        for e in events:
            if "segs" in e and "tStartMs" in e:
                text = "".join([seg.get("utf8", "") for seg in e["segs"]])
                start_sec = int(e["tStartMs"]) / 1000
                transcript.append({
                    "start_time": format_time(start_sec),
                    "link": f"https://www.youtube.com/watch?v={video_id}&t={int(start_sec)}s",
                    "text": text.strip()
                })

        os.remove(json_file)  # Clean up
        return transcript

    except Exception as e:
        return {"error": f"yt-dlp transcript error: {str(e)}"}
