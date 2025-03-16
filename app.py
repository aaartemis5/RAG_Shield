from flask import Flask, request, jsonify
from retriever import get_retriever
from prompt_llm import build_prompt, get_llm_response
from pymongo import MongoClient
from datetime import datetime
from config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION

app = Flask(__name__)

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]
chat_collection = db[MONGODB_COLLECTION]

@app.route("/", methods=["GET"])
def home():
    return "Backend is running. Use POST /query to get answers.", 200

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    user_query = data.get("query", "")
    if not user_query:
        return jsonify({"error": "Query not provided"}), 400

    try:
        retriever = get_retriever()
        docs = retriever.invoke(user_query)
        
        # Concatenate retrieved text from documents.
        context_parts = []
        for doc in docs:
            text = doc.metadata.get("text") if doc.metadata.get("text") else doc.page_content
            if text:
                context_parts.append(text)
        context = "\n\n".join(context_parts)
        
        final_prompt = build_prompt(user_query, context)
        answer = get_llm_response(final_prompt)
        
        # Save the chat session in MongoDB (each session is one exchange for simplicity)
        chat_document = {
            "session_id": datetime.utcnow().strftime("%Y%m%d%H%M%S%f"),
            "messages": [
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": answer}
            ],
            "timestamp": datetime.utcnow()
        }
        chat_collection.insert_one(chat_document)
        
        return jsonify({"answer": answer})
    except Exception as e:
        print("Error processing query:", e)
        return jsonify({"error": "Error processing query."}), 500

@app.route("/chats", methods=["GET"])
def get_chats():
    # Fetch the last 50 chat sessions, sorted by most recent.
    chats = list(chat_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(50))
    return jsonify(chats)

if __name__ == "__main__":
    # Disable reloader to avoid ECONNRESET issues.
    app.run(debug=True, use_reloader=False)
