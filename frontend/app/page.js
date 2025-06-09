"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function Home() {
  const [url, setUrl] = useState("");
  const [transcript, setTranscript] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const getTranscript = async () => {
    try {
      setLoading(true);
      setTranscript([]);
      setError(null);

      const response = await fetch("/api/transcript", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) throw new Error("Failed to fetch transcript");

      const data = await response.json();
      setTranscript(data.transcript || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const ingestTranscript = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error("Ingestion failed");
      }

      const data = await response.json();
      alert("✅ Transcript ingested and vector DB built!");
      console.log(data);
    } catch (err) {
      alert("❌ Failed to ingest transcript.");
      console.error(err);
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
      setAnswer(data.answer || "No answer found.");
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
              {loading ? "Loading..." : "Get Transcript"}
            </Button>
            <Button
              onClick={ingestTranscript}
              className="bg-green-600 text-white hover:bg-green-700 transition"
            >
              Ingest
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
