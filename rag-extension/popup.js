// For local testing, use your local backend URL
const backendUrl = "http://localhost:5000";

document.getElementById("sendBtn").addEventListener("click", async () => {
  const query = document.getElementById("query").value;
  if (!query.trim()) return;
  
  try {
    const res = await fetch(`${backendUrl}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query.trim() })
    });
    const data = await res.json();
    document.getElementById("response").innerText = data.answer || "No answer received.";
  } catch (err) {
    console.error("Error:", err);
    document.getElementById("response").innerText = "Error fetching response.";
  }
});
