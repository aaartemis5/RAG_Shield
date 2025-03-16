import json
import os
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from config import PINECONE_API_KEY, INDEX_NAME, EMBEDDING_MODEL

# -------------------- Initialize Pinecone --------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# -------------------- Load the Embedding Model --------------------
model = SentenceTransformer(EMBEDDING_MODEL)

# -------------------- Load Processed Record IDs --------------------
processed_ids_file = "processed_ids.json"
if os.path.exists(processed_ids_file):
    with open(processed_ids_file, "r") as f:
        processed_ids = json.load(f)
else:
    processed_ids = []

# -------------------- Load JSON Data --------------------
with open("data.json", "r") as f:
    records = json.load(f)

# -------------------- Generate Embeddings for New Records --------------------
new_vectors = []
new_ids = []
print("Generating embeddings for new records...")
for i, record in enumerate(records):
    record_id = f"record_{i}"
    if record_id in processed_ids:
        continue  # Skip records that have already been processed

    text = record.get("page_content", "")
    if not text:
        continue

    # Generate embedding using the specified model
    embedding = model.encode(text).tolist()

    # For debugging: print the first 5 dimensions for the first 2 new records
    if len(new_vectors) < 2:
        print(f"Embedding for {record_id} (first 5 dims): {embedding[:5]} ... (Total dimensions: {len(embedding)})")

    # Get metadata (if any) and ensure it contains a 'text' key with the document content
    metadata = record.get("metadata", {})
    metadata["text"] = text

    new_vectors.append((record_id, embedding, metadata))
    new_ids.append(record_id)

if new_vectors:
    upsert_response = index.upsert(vectors=new_vectors)
    print(f"Successfully inserted {len(new_vectors)} new vectors into Pinecone!")
    processed_ids.extend(new_ids)
    with open(processed_ids_file, "w") as f:
        json.dump(processed_ids, f)
else:
    print("No new records to process.")

# -------------------- Sample Query Demonstration --------------------
sample_query = "What suspicious IP addresses have been reported?"
print("\nProcessing sample query:")
print("User Query:", sample_query)
query_embedding = model.encode(sample_query).tolist()
print("Query Embedding (first 5 dims):", query_embedding[:5])
query_results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True
)
print("\nQuery Results:")
for match in query_results["matches"]:
    print(f"ID: {match['id']}, Score: {match['score']}")
    if "title" in match.get("metadata", {}):
        print(f"Title: {match['metadata']['title']}")
    snippet = match['metadata'].get("snippet", "") or "No snippet available."
    print("Snippet:", snippet)
    print("-" * 40)
