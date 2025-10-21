from qdrant_client import QdrantClient, models
from typing import List, Dict, Any
import os
import numpy as np

# Qdrant setup
QDRANT_CLIENT = QdrantClient(":memory:")  # In-memory for demo, use actual server in production
COLLECTION_NAME = "smartfolder_index"
VECTOR_DIMENSION = 384  # Updated to match our embedding dimension

def initialize_qdrant():
    """Initializes the Qdrant collection if it does not exist."""
    try:
        # Check if collection exists
        collections = QDRANT_CLIENT.get_collections()
        collection_exists = any(col.name == COLLECTION_NAME for col in collections.collections)
        
        if not collection_exists:
            QDRANT_CLIENT.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=VECTOR_DIMENSION, 
                    distance=models.Distance.COSINE
                ),
            )
            print(f"Qdrant collection '{COLLECTION_NAME}' created.")
        else:
            print(f"Qdrant collection '{COLLECTION_NAME}' already exists.")
            
    except Exception as e:
        print(f"Error initializing Qdrant: {e}")
        raise

def index_file_record(record: Dict[str, Any]):
    """Indexes a single file record into the Qdrant vector store."""
    embedding_vector = record.get("embedding_vector")
    if not embedding_vector:
        return
    
    try:
        # Ensure vector is the right size
        if len(embedding_vector) != VECTOR_DIMENSION:
            print(f"Warning: Vector dimension mismatch. Expected {VECTOR_DIMENSION}, got {len(embedding_vector)}")
            return
        
        # Create a point for Qdrant
        point_id = abs(hash(record["path"])) % (2**63)  # Ensure positive ID
        
        point = models.PointStruct(
            id=point_id,
            vector=embedding_vector,
            payload={
                "path": record["path"],
                "filename": record["filename"],
                "file_type": record.get("file_type", "unknown"),
                "size": record.get("size", 0),
                "hash": record.get("hash", ""),
                "text_content": record.get("text_content", "")[:1000],  # Limit payload size
                "faces_detected": record.get("faces_detected", [])
            }
        )
        
        QDRANT_CLIENT.upsert(
            collection_name=COLLECTION_NAME,
            points=[point],
            wait=True
        )
        
    except Exception as e:
        print(f"Error indexing {record['filename']} to Qdrant: {e}")

def search_qdrant(query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
    """Performs a vector search in Qdrant."""
    try:
        # Ensure query vector is the right size
        if len(query_vector) != VECTOR_DIMENSION:
            print(f"Warning: Query vector dimension mismatch. Expected {VECTOR_DIMENSION}, got {len(query_vector)}")
            return []
        
        search_result = QDRANT_CLIENT.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True,
            score_threshold=0.1  # Minimum similarity threshold
        )
        
        results = []
        for hit in search_result:
            result = {
                "path": hit.payload.get("path", ""),
                "filename": hit.payload.get("filename", ""),
                "file_type": hit.payload.get("file_type", "unknown"),
                "size": hit.payload.get("size", 0),
                "score": hit.score,
                "snippet": hit.payload.get("text_content", "")[:200] + "..." if hit.payload.get("text_content") else "",
                "faces_detected": hit.payload.get("faces_detected", [])
            }
            results.append(result)
            
        return results
        
    except Exception as e:
        print(f"Error searching Qdrant: {e}")
        return []

def get_collection_info():
    """Get information about the current collection."""
    try:
        info = QDRANT_CLIENT.get_collection(COLLECTION_NAME)
        return {
            "status": info.status,
            "vectors_count": info.vectors_count,
            "indexed_vectors_count": info.indexed_vectors_count,
            "points_count": info.points_count
        }
    except Exception as e:
        print(f"Error getting collection info: {e}")
        return {}

def clear_collection():
    """Clear all points from the collection (useful for testing)."""
    try:
        QDRANT_CLIENT.delete_collection(COLLECTION_NAME)
        initialize_qdrant()
        print("Collection cleared and reinitialized.")
    except Exception as e:
        print(f"Error clearing collection: {e}")