"""
Ingests policy documents into a ChromaDB vector database.
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer


def ingest_policies() -> None:
    """Embeds and loads policy documents into ChromaDB."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(base_dir, "docs")
    db_dir = os.path.join(base_dir, "chroma_db")

    # Ensure docs directory exists
    if not os.path.exists(docs_dir):
        print(f"Error: Docs directory not found at {docs_dir}")
        return

    documents = []
    ids = []
    metadatas = []

    # Read policy docs
    for i in range(1, 9):
        filename = f"doc_0{i}.txt"
        filepath = os.path.join(docs_dir, filename)
        if not os.path.exists(filepath):
            print(f"Warning: File {filename} not found at {filepath}. Skipping.")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()

        documents.append(content)
        ids.append(filename)
        metadatas.append({"source": filename})

    print(f"Loaded {len(documents)} documents for ingestion.")

    # Load model
    print("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Generate embeddings
    print("Generating embeddings for policy documents...")
    embeddings = model.encode(documents)
    embeddings_list = [emb.tolist() for emb in embeddings]

    # Connect to ChromaDB
    print(f"Connecting to persistent ChromaDB at: {db_dir}")
    client = chromadb.PersistentClient(path=db_dir)

    collection_name = "zepto_policies"

    # Reset collection
    try:
        client.delete_collection(collection_name)
        print(f"Cleared existing '{collection_name}' collection.")
    except Exception:
        # Collection didn't exist yet
        pass

    # Create collection
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    # Add to collection
    collection.add(
        ids=ids,
        embeddings=embeddings_list,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Successfully ingested {len(documents)} policies into Chroma collection '{collection_name}'.\n")


if __name__ == "__main__":
    ingest_policies()
