import numpy as np
import os
import base64
from typing import List, Dict, Any
from sklearn.cluster import DBSCAN
from collections import defaultdict
import random
from PIL import Image
import io

# Store face data with image references
FACE_DATABASE = []  # List of dicts: {cluster_id, encoding, image_path, thumbnail}
NEXT_CLUSTER_ID = 1

def create_thumbnail(image_path: str, size: tuple = (150, 150)) -> str:
    """Creates a base64 encoded thumbnail of an image."""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size)
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Save to bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            # Encode to base64
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            return f"data:image/jpeg;base64,{img_base64}"
    except Exception as e:
        print(f"Error creating thumbnail for {image_path}: {e}")
        return None

def detect_and_encode_faces(image_path: str) -> List[Dict[str, Any]]:
    """
    Enhanced: Detects faces in an image and returns face data with metadata.
    In a real app, this would use face_recognition or similar library.
    """
    if not os.path.exists(image_path):
        return []
    
    # Check if it's actually an image file
    try:
        with Image.open(image_path) as img:
            pass  # Just verify it's a valid image
    except:
        return []
    
    # Simulate face detection (30% chance of finding 1-2 faces in images)
    if random.random() > 0.7:
        return []
    
    num_faces = random.randint(1, 2)
    faces_data = []
    
    for _ in range(num_faces):
        # Generate mock 128-dimension encoding
        encoding = [random.uniform(-1, 1) for _ in range(128)]
        
        face_data = {
            'encoding': encoding,
            'image_path': image_path,
            'thumbnail': create_thumbnail(image_path)
        }
        faces_data.append(face_data)
    
    return faces_data

def cluster_faces(faces_data: List[Dict[str, Any]]) -> List[int]:
    """
    Enhanced: Clusters face encodings and stores them with image references.
    """
    global FACE_DATABASE, NEXT_CLUSTER_ID
    
    if not faces_data:
        return []
    
    assigned_cluster_ids = []
    
    for face_data in faces_data:
        encoding = face_data['encoding']
        
        # Simple similarity check with existing faces
        cluster_id = None
        
        # Check against existing faces (simplified clustering)
        for existing_face in FACE_DATABASE:
            # Calculate similarity (mock distance calculation)
            distance = sum((a - b) ** 2 for a, b in zip(encoding, existing_face['encoding'])) ** 0.5
            
            # If similar enough (threshold), assign to same cluster
            if distance < 50:  # Mock threshold
                cluster_id = existing_face['cluster_id']
                break
        
        # If no similar face found, create new cluster
        if cluster_id is None:
            cluster_id = NEXT_CLUSTER_ID
            NEXT_CLUSTER_ID += 1
        
        # Add to database
        face_record = {
            'cluster_id': cluster_id,
            'encoding': encoding,
            'image_path': face_data['image_path'],
            'thumbnail': face_data['thumbnail']
        }
        FACE_DATABASE.append(face_record)
        assigned_cluster_ids.append(cluster_id)
    
    return assigned_cluster_ids

def get_face_clusters_summary() -> List[Dict[str, Any]]:
    """Enhanced: Returns face clusters with representative thumbnails."""
    cluster_data = defaultdict(list)
    
    # Group faces by cluster_id
    for face in FACE_DATABASE:
        cluster_data[face['cluster_id']].append(face)
    
    summary = []
    for cluster_id, faces in cluster_data.items():
        # Use first face as representative thumbnail
        representative_face = faces[0]
        
        cluster_info = {
            "cluster_id": cluster_id,
            "name": f"Person {cluster_id}",
            "count": len(faces),
            "thumbnail": representative_face['thumbnail'],
            "sample_images": [face['image_path'] for face in faces[:3]]  # Up to 3 sample images
        }
        summary.append(cluster_info)
    
    return summary

def get_images_for_cluster(cluster_id: int) -> List[Dict[str, Any]]:
    """Get all images for a specific face cluster."""
    cluster_images = []
    for face in FACE_DATABASE:
        if face['cluster_id'] == cluster_id:
            cluster_images.append({
                'path': face['image_path'],
                'thumbnail': face['thumbnail']
            })
    return cluster_images

def clear_face_database():
    """Clear all face data (useful for testing)."""
    global FACE_DATABASE, NEXT_CLUSTER_ID
    FACE_DATABASE = []
    NEXT_CLUSTER_ID = 1