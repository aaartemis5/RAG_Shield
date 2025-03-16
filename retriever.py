import os
from RagShield.config import INDEX_NAME, PINECONE_API_KEY, PINECONE_ENVIRONMENT, EMBEDDING_MODEL
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["PINECONE_ENVIRONMENT"] = PINECONE_ENVIRONMENT

from langchain_community.vectorstores import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
import pinecone

# Initialize Pinecone client
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

def get_retriever():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = Pinecone.from_existing_index(INDEX_NAME, embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    return retriever

if __name__ == "__main__":
    retriever = get_retriever()
    test_query = "What suspicious IP addresses are reported?"
    docs = retriever.invoke(test_query)
    for i, doc in enumerate(docs):
        text = doc.metadata.get("text") if "text" in doc.metadata and doc.metadata.get("text") else doc.page_content
        print(f"Doc {i+1}: {text[:200]}...\n")
