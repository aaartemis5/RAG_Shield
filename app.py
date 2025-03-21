import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # Enable CORS for cross-origin requests
from retriever import get_retriever
from prompt_llm import build_prompt, get_llm_response
from pymongo import MongoClient
from datetime import datetime
import uuid
from config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION

app = Flask(__name__)
CORS(app)  # Allow all origins; adjust if needed for production

# Initialize MongoDB client and collection
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
    chat_id = data.get("chat_id")  # Provided if continuing a session

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

        if chat_id:
            # Update existing session by appending new messages.
            chat_collection.update_one(
                {"session_id": chat_id},
                {"$push": {"messages": {"$each": [
                    {"role": "user", "content": user_query},
                    {"role": "assistant", "content": answer}
                ]}},
                 "$set": {"timestamp": datetime.utcnow()}}
            )
        else:
            # Create a new session with a unique ID and friendly title.
            chat_id = str(uuid.uuid4())
            title = user_query if len(user_query) <= 30 else user_query[:30].strip() + "..."
            chat_document = {
                "session_id": chat_id,
                "title": title,
                "messages": [
                    {"role": "user", "content": user_query},
                    {"role": "assistant", "content": answer}
                ],
                "timestamp": datetime.utcnow()
            }
            chat_collection.insert_one(chat_document)

        return jsonify({"answer": answer, "chat_id": chat_id})
    except Exception as e:
        print("Error processing query:", e)
        return jsonify({"error": "Error processing query."}), 500

@app.route("/chats", methods=["GET"])
def get_chats():
    # Fetch all chat sessions, sorted by most recent.
    chats = list(chat_collection.find({}, {"_id": 0}).sort("timestamp", -1))
    return jsonify(chats)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=port)
