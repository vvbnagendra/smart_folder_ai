import numpy as np
from typing import List, Dict, Any
from sklearn.cluster import DBSCAN
from collections import defaultdict
import random

# Placeholder for storing known face encodings and their cluster IDs
# In a real app, this would be persisted in the database
KNOWN_FACES = []
KNOWN_IDS = []
NEXT_CLUSTER_ID = 1

def detect_and_encode_faces(image_path: str) -> List[List[float]]:
    """
    MOCK: Detects faces in an image and returns their 128-dimension encodings.
    In a real app, this would use a library like face_recognition or DeepFace.
    """
    # Simulate a random number of faces detected (0 to 2)
    num_faces = random.randint(0, 2)
    
    encodings = []
    for _ in range(num_faces):
        # Generate a mock 128-dimension encoding vector
        mock_encoding = [random.uniform(-1, 1) for _ in range(128)]
        encodings.append(mock_encoding)
        
    return encodings

def cluster_faces(new_encodings: List[List[float]]) -> List[int]:
    """
    MOCK: Clusters new face encodings with known faces.
    This is a simplified, in-memory clustering logic for the minimal implementation.
    """
    global KNOWN_FACES, KNOWN_IDS, NEXT_CLUSTER_ID
    
    if not new_encodings:
        return []

    assigned_cluster_ids = []
    
    for new_encoding in new_encodings:
        # Simple clustering logic: if a new face is "close" to a known face, assign the same ID
        is_new_person = True
        
        # In a real app, this would be a proper DBSCAN or k-means clustering
        # For the mock, we'll just assign a new ID every time to simulate detection
        
        assigned_id = NEXT_CLUSTER_ID
        NEXT_CLUSTER_ID += 1
        assigned_cluster_ids.append(assigned_id)
        
        # Update KNOWN_FACES and KNOWN_IDS with the new face
        KNOWN_FACES.append(new_encoding)
        KNOWN_IDS.append(assigned_id)

    return assigned_cluster_ids

def get_face_clusters_summary() -> List[Dict[str, Any]]:
    """Generates a summary of the current face clusters."""
    cluster_counts = defaultdict(int)
    for cluster_id in KNOWN_IDS:
        cluster_counts[cluster_id] += 1
        
    summary = []
    for cluster_id, count in cluster_counts.items():
        # Assign a placeholder name for the cluster ID
        name = f"Person {cluster_id}"
        summary.append({"cluster_id": cluster_id, "name": name, "count": count})
        
    return summary

if __name__ == "__main__":
    print("Face Cluster Engine Initialized (MOCK).")
    
    # Simulate a few scans
    print("\n--- First Image Scan (MOCK)")
    encodings_1 = detect_and_encode_faces("dummy_path_1.jpg")
    cluster_ids_1 = cluster_faces(encodings_1)
    print(f"Detected {len(encodings_1)} faces. Assigned IDs: {cluster_ids_1}")
    print(f"Summary: {get_face_clusters_summary()}")
    
    print("\n--- Second Image Scan (MOCK)")
    encodings_2 = detect_and_encode_faces("dummy_path_2.jpg")
    cluster_ids_2 = cluster_faces(encodings_2)
    print(f"Detected {len(encodings_2)} faces. Assigned IDs: {cluster_ids_2}")
    print(f"Summary: {get_face_clusters_summary()}")

