from qdrant_client import QdrantClient, models
from typing import List, Dict, Any
import os

# Placeholder for Qdrant setup
QDRANT_CLIENT = QdrantClient(":memory:")
COLLECTION_NAME = "smartfolder_index"
VECTOR_DIMENSION = 4 # Matches the placeholder vector size in scanner.py

def initialize_qdrant():
    """Initializes the Qdrant collection if it does not exist."""
    try:
        QDRANT_CLIENT.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=VECTOR_DIMENSION, distance=models.Distance.COSINE),
        )
        print(f"Qdrant collection '{COLLECTION_NAME}' initialized.")
    except Exception as e:
        print(f"Error initializing Qdrant: {e}")

def index_file_record(record: Dict[str, Any]):
    """Indexes a single file record into the Qdrant vector store."""
    if record.get("embedding_vector"):
        try:
            # Create a point for Qdrant
            point = models.PointStruct(
                id=hash(record["path"]), # Use hash of path as a unique ID
                vector=record["embedding_vector"],
                payload={
                    "path": record["path"],
                    "filename": record["filename"],
                    "hash": record["hash"],
                    "text_content": record["text_content"]
                }
            )
            
            QDRANT_CLIENT.upsert(
                collection_name=COLLECTION_NAME,
                points=[point],
                wait=True
            )
            print(f"Indexed: {record['filename']}")
        except Exception as e:
            print(f"Error indexing {record['filename']} to Qdrant: {e}")

def search_qdrant(query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """Performs a vector search in Qdrant."""
    try:
        search_result = QDRANT_CLIENT.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True
        )
        
        results = []
        for hit in search_result:
            results.append({
                "path": hit.payload["path"],
                "filename": hit.payload["filename"],
                "score": hit.score,
                "snippet": hit.payload["text_content"][:100] + "..."
            })
        return results
    except Exception as e:
        print(f"Error searching Qdrant: {e}")
        return []

if __name__ == "__main__":
    # Example Usage
    initialize_qdrant()
    
    # Simulate a file record from scanner.py
    sample_record = {
        "path": "/data/test_document.txt",
        "filename": "test_document.txt",
        "size": 100,
        "mtime": 1678886400,
        "hash": "a1b2c3d4e5f6",
        "indexed": True,
        "text_content": "This document is about the new project strategy and its key milestones.",
        "embedding_vector": [0.1, 0.2, 0.3, 0.4],
        "faces_detected": []
    }
    
    index_file_record(sample_record)
    
    # Simulate a query vector (for semantic search)
    query_vector = [0.11, 0.19, 0.32, 0.41]
    
    search_results = search_qdrant(query_vector, top_k=1)
    print("\nSemantic Search Results:")
    for result in search_results:
        print(f"  - {result['filename']} (Score: {result['score']:.4f})")

