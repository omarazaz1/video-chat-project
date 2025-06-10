import urllib.parse
import subprocess
import json
import os

def extract_video_id(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if "youtube.com" in parsed.netloc:
        return urllib.parse.parse_qs(parsed.query).get("v", [None])[0]
    elif "youtu.be" in parsed.netloc:
        return parsed.path.strip("/")
    return None

def format_time(seconds: float) -> str:
    return f"{int(seconds) // 60:02}:{int(seconds) % 60:02}"

def get_youtube_transcript(url: str):
    try:
        video_id = extract_video_id(url)
        print("🎯 Extracted video ID:", video_id)
        if not video_id:
            return {"error": "Invalid YouTube URL. Could not extract video ID."}

       
        subprocess.run([
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", "en",
            "--skip-download",
            "--sub-format", "json3",
            "-o", f"{video_id}.%(ext)s",
            url
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Look for subtitle file
        subtitle_file = None
        for ext in ["en.json3", "en-US.json3"]:
            test_file = f"{video_id}.{ext}"
            if os.path.exists(test_file):
                subtitle_file = test_file
                break

        if not subtitle_file:
            return {"error": "No subtitles found after running yt-dlp."}

        with open(subtitle_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        events = data.get("events", [])
        transcript = []
        for e in events:
            if "segs" in e and "tStartMs" in e:
                text = "".join(seg.get("utf8", "") for seg in e["segs"])
                if text.strip():
                    start_sec = int(e["tStartMs"]) / 1000
                    transcript.append({
                        "start_time": format_time(start_sec),
                        "link": f"https://www.youtube.com/watch?v={video_id}&t={int(start_sec)}s",
                        "text": text.strip()
                    })

        os.remove(subtitle_file)
        return transcript

    except Exception as e:
        return {"error": f"Transcript extraction failed: {str(e)}"}
