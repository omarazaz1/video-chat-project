export async function POST(req) {
    try {
        const { url } = await req.json();

        const response = await fetch("http://localhost:8000/transcript", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url }),
        });

        if (!response.ok) throw new Error("Failed to fetch transcript");

        const data = await response.json();
        return Response.json({ transcript: data.transcript });
    } catch (err) {
        return new Response(
            JSON.stringify({ error: "Failed to process request" }),
            { status: 400 }
        );
    }
}
