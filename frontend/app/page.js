
"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function page() {
  const [url, setUrl] = useState("");
  const [videoId, setVideoId] = useState("");
  const [transcript, setTranscript] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const extractVideoId = (url) => {

    const match = url.match(/(?:v=|\/)([0-9A-Za-z_-]{11})/);
    return match?.[1] || "";
  };

  const getTranscript = async () => {
    try {
      setLoading(true);
      setTranscript([]);
      setError(null);

      const id = extractVideoId(url);
      if (!id) {
        alert("❌ Invalid YouTube URL");
        return;
      }
      setVideoId(id);

      const response = await fetch("/api/transcript", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (data.transcript?.error) {
        setError(data.transcript.error);
        alert("❌ Error: " + data.transcript.error);
        return;
      }

      if (!Array.isArray(data.transcript)) {
        throw new Error("Transcript format is invalid.");
      }

      setTranscript(data.transcript);

      const ingestRes = await fetch("http://127.0.0.1:8000/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript: data.transcript }),
      });

      if (!ingestRes.ok) throw new Error("Ingest failed");

      // alert("✅ Transcript fetched & ingested!");            {PR}


    } catch (err) {

      setError(err.message);
      alert("❌ " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async () => {
    setAnswer("");
    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();
      setAnswer(data.answer?.result || "No answer found.");
    } catch (err) {
      setAnswer("Error fetching answer.");
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-6">
      <Card className="w-full max-w-2xl shadow-2xl border-none">
        <CardContent className="space-y-6 p-6">
          <h1 className="text-3xl font-bold text-center text-black drop-shadow-lg">
            🎬 YouTube Transcript Viewer
          </h1>

          {videoId && (
            <div className="w-full aspect-video rounded-xl overflow-hidden shadow-lg border border-white/30">
              <iframe
                src={`https://www.youtube.com/embed/${videoId}`}
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="w-full h-full"
              ></iframe>
            </div>
          )}

          <div className="flex items-center gap-3">
            <Input
              placeholder="Paste YouTube URL..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-grow bg-white/80 backdrop-blur text-black border-0 focus:ring-2 focus:ring-white"
            />
            <Button
              onClick={getTranscript}
              disabled={loading}
              className="bg-black text-white hover:bg-white hover:text-black transition"
            >
              {loading ? "Loading..." : "Analyze Video"}
            </Button>
          </div>

          {error && <p className="text-red-500">{error}</p>}

          {transcript.length > 0 && (
            <div className="max-h-[400px] overflow-y-auto bg-white/90 p-4 rounded-lg text-sm text-black space-y-2">
              {transcript.map((item, index) => (
                <p key={index} className="text-black">
                  <a
                    href={item.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 font-medium hover:underline"
                  >
                    [{item.start_time}]
                  </a>{" "}
                  {item.text}
                </p>
              ))}
            </div>
          )}

          {transcript.length > 0 && (
            <div className="space-y-4 pt-6">
              <Input
                placeholder="Ask a question about the video..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="bg-white/80 backdrop-blur text-black border-0"
              />
              <Button
                onClick={askQuestion}
                className="bg-indigo-600 text-white hover:bg-white hover:text-indigo-600 transition"
              >
                Ask
              </Button>
              {answer && (
                <div className="bg-white/90 p-4 rounded-lg text-sm text-black space-y-2 shadow">
                  <p className="font-semibold text-indigo-600">Answer:</p>
                  <p>{answer}</p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
