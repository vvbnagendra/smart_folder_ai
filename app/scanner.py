import os
import hashlib
import json
from typing import List, Dict, Any, Optional
from .ocr_engine import ocr_file
from .face_cluster import detect_and_encode_faces, cluster_faces

# Placeholder for the index file
INDEX_FILE = "smartfolder_index.json"

def calculate_hash(filepath: str) -> str:
    """Calculates the SHA256 hash of a file for duplicate detection."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as file:
            while True:
                chunk = file.read(4096)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {filepath}: {e}")
        return ""

def process_file_content(filepath: str) -> Dict[str, Any]:
    """
    Placeholder for sending content to OCR/embedding service.
    This function will be expanded in later phases.
    """
    # Simulate content extraction and embedding
    # In a real app, this would call ocr_engine.py or an embedding service
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    content_data = {
        "text_content": "",
        "embedding_vector": None,
        "faces_detected": []
    }
    
    if ext in ['.txt', '.md', '.pdf']:
        content_data["text_content"] = f"Simulated text content from {os.path.basename(filepath)}."
    elif ext in ['.jpg', '.jpeg', '.png']:
        content_data["text_content"] = f"Simulated OCR text for image {os.path.basename(filepath)}."
        content_data["faces_detected"] = ["person_a", "person_b"] # Placeholder
        
    # --- Content Processing ---
    
    # --- Content Processing ---
    
    # 1. OCR for text extraction
    text_content = ocr_file(filepath)
    
    # 2. Face Detection
    face_encodings = []
    if ext in ['.jpg', '.jpeg', '.png']:
        face_encodings = detect_and_encode_faces(filepath)
        
        # Cluster the detected faces (this updates the global KNOWN_FACES/KNOWN_IDS in face_cluster.py)
        cluster_faces(face_encodings)
        
    # 3. Embedding Generation (Simulated)
    if text_content or face_encodings:
        content_data["text_content"] = text_content
        content_data["faces_detected"] = face_encodings
        
        # Simulate embedding generation based on content
        # In a real app, this would call an embedding model (e.g., CLIP, OpenAI)
        # For simplicity, we'll use a fixed placeholder vector for all indexed items
        content_data["embedding_vector"] = [0.1, 0.2, 0.3, 0.4] # Placeholder vector


        
    return content_data

def scan_directory(scan_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Walks directories, collects metadata, hashes, and prepares content for indexing.
    """
    index_data = []
    
    for root_path in scan_paths:
        if not os.path.isdir(root_path):
            print(f"Warning: Scan path not found: {root_path}")
            continue

        print(f"Scanning directory: {root_path}")
        
        for root, _, files in os.walk(root_path):
            for file in files:
                filepath = os.path.join(root, file)
                
                # Skip the index file itself if it's in the scan path
                if file == INDEX_FILE:
                    continue
                    
                # Collect basic metadata
                stat = os.stat(filepath)
                
                file_record = {
                    "path": filepath,
                    "filename": file,
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "hash": calculate_hash(filepath),
                    "indexed": False # Flag to track if content has been processed
                }
                
                # Only process content for files that are not empty and have a hash
                if file_record["size"] > 0 and file_record["hash"]:
                    content_data = process_file_content(filepath)
                    file_record.update(content_data)
                    file_record["indexed"] = True
                
                index_data.append(file_record)
                
    return index_data

def save_index(data: List[Dict[str, Any]]):
    """Saves the index data to a JSON file."""
    try:
        with open(INDEX_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Index saved to {INDEX_FILE}")
    except Exception as e:
        print(f"Error saving index: {e}")

def load_index() -> List[Dict[str, Any]]:
    """Loads the index data from a JSON file."""
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading index: {e}")
    return []

if __name__ == "__main__":
    # Example usage: simulate a scan path
    # In the Docker environment, /data will be the mounted volume
    scan_paths = ["/data"] 
    
    # Example usage: simulate a scan path
    # In the Docker environment, /data will be the mounted volume
    scan_paths = ["/data"] 
    
    # Create a dummy file for testing
    os.makedirs("/data", exist_ok=True)
    
    # Create dummy files for testing different processors
    with open("/data/doc_for_ocr.png", "w") as f:
        f.write("Dummy image content") # Not a real image, but simulates the file path
    with open("/data/photo_with_face.jpg", "w") as f:
        f.write("Dummy image content") # Not a real image, but simulates the file path
    with open("/data/simple_text.txt", "w") as f:
        f.write("This is a simple text document.")
        
    index = scan_directory(scan_paths)
    save_index(index)
    
    # Example of loaded data
    loaded_index = load_index()
    print(f"\nLoaded {len(loaded_index)} records from index.")
    
    # Clean up dummy files
    os.remove("/data/doc_for_ocr.png")
    os.remove("/data/photo_with_face.jpg")
    os.remove("/data/simple_text.txt")
    os.rmdir("/data")

