import os
from pinecone import Pinecone
from config import PINECONE_API_KEY, PINECONE_ENVIRONMENT, INDEX_NAME

def initialize_pinecone():
    # Create an instance of the Pinecone client
    pc = Pinecone(api_key=PINECONE_API_KEY)
    indexes = pc.list_indexes().names()
    if INDEX_NAME not in indexes:
        print(f"Index '{INDEX_NAME}' not found. Please create it via the Pinecone Console or CLI.")
    else:
        print(f"Index '{INDEX_NAME}' found. Pinecone is ready to use.")

if __name__ == "__main__":
    initialize_pinecone()
