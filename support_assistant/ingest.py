"""
Ingestion Module

Loads customer support policy text files, generates local embeddings using sentence-transformers,
and stores them in a persistent ChromaDB vector store collection.
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer


def ingest_policies() -> None:
    """
    Reads doc_01.txt through doc_08.txt, embeds their text contents,
    and populates the 'zepto_policies' persistent Chroma collection.
    """
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

    # Read doc_01.txt to doc_08.txt verbatim
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

    # Load local SentenceTransformer embedding model
    print("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Generate embeddings
    print("Generating embeddings for policy documents...")
    embeddings = model.encode(documents)
    # Convert numpy arrays to lists for Chroma compatibility
    embeddings_list = [emb.tolist() for emb in embeddings]

    # Initialize persistent Chroma client
    print(f"Connecting to persistent ChromaDB at: {db_dir}")
    client = chromadb.PersistentClient(path=db_dir)

    collection_name = "zepto_policies"

    # Drop existing collection to ensure ingestion idempotence and clean state
    try:
        client.delete_collection(collection_name)
        print(f"Cleared existing '{collection_name}' collection.")
    except Exception:
        # Collection didn't exist yet
        pass

    # Create new collection with cosine distance metric space
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    # Insert items
    collection.add(
        ids=ids,
        embeddings=embeddings_list,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Successfully ingested {len(documents)} policies into Chroma collection '{collection_name}'.\n")


if __name__ == "__main__":
    ingest_policies()
