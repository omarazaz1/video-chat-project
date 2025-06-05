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

  const getTranscript = async () => {
    try {
      setLoading(true);
      setTranscript([]);
      setError(null);

      const response = await fetch("/api/transcript", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }), // ✅ Important: send { url } object
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
          </div>
          {error && <p className="text-red-500">{error}</p>}
          {transcript.length > 0 && (
            <div className="max-h-[400px] overflow-y-auto bg-white/90 p-4 rounded-lg text-sm text-black space-y-2">
              {/* {transcript.map((item, index) => (
                <p key={index}>
                  <span className="font-semibold text-indigo-600 mr-2">
                    [{item.start_time}]
                  </span>
                  {item.text}
                </p>
              ))} */}
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
        </CardContent>
      </Card>
    </main>
  );
}
