import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .scanner import scan_directory, load_index
from .indexer import initialize_qdrant, index_file_record, search_qdrant
from .face_cluster import get_face_clusters_summary
from dotenv import load_dotenv

# Load environment variables from sample.env
load_dotenv(dotenv_path="sample.env")

app = FastAPI(title="Smart Folder Organizer API")

# --- Configuration ---
SCAN_PATHS = os.getenv("SCAN_PATHS", "/data").split(":")
# DB_URL = os.getenv("DB_URL", "sqlite:///./smartfolder.db") # Using a simple SQLite for minimal setup
# QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")


# --- Placeholder for Core Services (to be implemented in later phases) ---
def start_scan_process():
    """Starts the scanner.py process, collects metadata, and indexes content."""
    print(f"Starting full scan of paths: {SCAN_PATHS}")
    
    # 1. Scan and collect data
    file_records = scan_directory(SCAN_PATHS)
    
    # 2. Index content
    initialize_qdrant()
    for record in file_records:
        if record.get("indexed"):
            index_file_record(record)
            
    return {"status": "Scan and indexing complete", "total_files": len(file_records)}

def perform_search(query: str, search_type: str):
    """Performs keyword or semantic search."""
    
    if search_type == "keyword":
        # For keyword search, we'll search the in-memory index loaded by scanner.py (simplification)
        # In a real app, this would query PostgreSQL or Qdrant's keyword search
        full_index = load_index()
        results = []
        for record in full_index:
            # Check for keyword in filename or text content
            if (query.lower() in record["filename"].lower() or 
                query.lower() in record.get("text_content", "").lower()):
                results.append({
                    "filename": record["filename"],
                    "path": record["path"],
                    "snippet": record.get("text_content", "")[:100] + "...",
                    "type": "document" if ".txt" in record["filename"] else "image"
                })
        return results
        
    elif search_type == "semantic":
        # Simulate query embedding for semantic search
        # In a real app, this would call the same embedding model as the indexer
        query_vector = [0.11, 0.19, 0.32, 0.41] # Placeholder
        
        # Search Qdrant
        results = search_qdrant(query_vector, top_k=5)
        return results
        
    return []

def list_face_clusters():
    """Returns the summary of detected face clusters."""
    return get_face_clusters_summary()


# --- API Endpoints ---

class SearchRequest(BaseModel):
    query: str
    search_type: str = "keyword" # keyword or semantic

@app.post("/api/scan")
def scan_folders():
    """Starts the recursive folder scan and indexing process."""
    return start_scan_process()

@app.post("/api/search")
def search_files(request: SearchRequest):
    """Performs keyword or semantic search."""
    return perform_search(request.query, request.search_type)

@app.get("/api/faces")
def get_face_clusters():
    """Lists all detected face clusters."""
    return list_face_clusters()

@app.get("/api/organize")
def get_organize_suggestions():
    """Provides suggestions for file cleanup and renaming."""
    return {"suggestions": [
        {"file": "IMG_1234.jpg", "suggestion": "Rename to 'Meeting_Notes_2024-10-15.jpg'"},
        {"file": "Copy_of_Doc.docx", "suggestion": "Duplicate of 'Original_Doc.docx'. Delete or archive."}
    ]}

@app.get("/api/status")
def get_status():
    """Returns the current status of the system."""
    return {"status": "online", "scan_paths": SCAN_PATHS}


# --- Serve Frontend Static Files ---
# The Dockerfile copies the built React app to /app/app/static
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

