import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.scanner import scan_directory, load_index, search_files
from app.indexer import initialize_qdrant, index_file_record, search_qdrant
from app.face_cluster import get_face_clusters_summary, get_images_for_cluster
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv(dotenv_path="sample.env")

app = FastAPI(title="Smart Folder Organizer API")

# --- Configuration ---
SCAN_PATHS = os.getenv("SCAN_PATHS", "/data").split(":")

# Global state
current_index = []

# --- Request Models ---
class SearchRequest(BaseModel):
    query: str
    search_type: str = "keyword"  # keyword or semantic

class FaceClusterRequest(BaseModel):
    cluster_id: int

# --- Utility Functions ---
def get_scan_status():
    """Get current scan status and statistics."""
    try:
        if os.path.exists("scan_summary.json"):
            with open("scan_summary.json", 'r') as f:
                summary = json.load(f)
            return summary
        else:
            return {"total_files": 0, "indexed_files": 0, "file_types": {}}
    except Exception:
        return {"total_files": 0, "indexed_files": 0, "file_types": {}}

# --- API Endpoints ---

@app.post("/api/scan")
def scan_folders():
    """Starts the recursive folder scan and indexing process."""
    global current_index
    
    try:
        print(f"Starting scan of paths: {SCAN_PATHS}")
        
        # Perform the scan
        file_records = scan_directory(SCAN_PATHS)
        current_index = file_records
        
        # Save the index
        from .scanner import save_index
        save_index(file_records)
        
        # Initialize Qdrant and index content
        try:
            initialize_qdrant()
            indexed_count = 0
            for record in file_records:
                if record.get("indexed") and record.get("embedding_vector"):
                    index_file_record(record)
                    indexed_count += 1
        except Exception as e:
            print(f"Warning: Vector indexing failed: {e}")
            indexed_count = 0
        
        # Get final statistics
        stats = get_scan_status()
        
        return {
            "status": "Scan and indexing complete", 
            "total_files": len(file_records),
            "indexed_files": len([r for r in file_records if r.get("indexed", False)]),
            "vector_indexed": indexed_count,
            "file_types": stats.get("file_types", {}),
            "scan_paths": SCAN_PATHS
        }
        
    except Exception as e:
        print(f"Error during scan: {e}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

@app.post("/api/search")
def search_files_endpoint(request: SearchRequest):
    """Performs keyword or semantic search."""
    global current_index
    
    try:
        # Load index if not in memory
        if not current_index:
            current_index = load_index()
        
        if not current_index:
            return {"error": "No index found. Please run a scan first.", "results": []}
        
        # Perform search using the enhanced search function
        results = search_files(request.query, request.search_type)
        
        # Format results for frontend
        formatted_results = []
        for record in results:
            result_item = {
                "filename": record.get("filename", ""),
                "path": record.get("path", ""),
                "file_type": record.get("file_type", "unknown"),
                "size": record.get("size", 0),
                "snippet": record.get("text_content", "")[:200] + "..." if record.get("text_content") else "",
                "relevance": record.get("relevance", 0.0)
            }
            
            # Add score for semantic search
            if request.search_type == "semantic":
                result_item["score"] = record.get("relevance", 0.0)
            
            formatted_results.append(result_item)
        
        return formatted_results
        
    except Exception as e:
        print(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/faces")
def get_face_clusters():
    """Lists all detected face clusters with thumbnails."""
    try:
        clusters = get_face_clusters_summary()
        return clusters
    except Exception as e:
        print(f"Error getting face clusters: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get face clusters: {str(e)}")

@app.post("/api/faces/{cluster_id}")
def get_face_cluster_images(cluster_id: int):
    """Get all images for a specific face cluster."""
    try:
        images = get_images_for_cluster(cluster_id)
        return {"cluster_id": cluster_id, "images": images}
    except Exception as e:
        print(f"Error getting cluster images: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cluster images: {str(e)}")

@app.get("/api/organize")
def get_organize_suggestions():
    """Provides suggestions for file cleanup and renaming."""
    global current_index
    
    try:
        if not current_index:
            current_index = load_index()
        
        suggestions = []
        
        # Find potential duplicates based on hash
        hash_groups = {}
        for record in current_index:
            file_hash = record.get("hash")
            if file_hash and file_hash != "":
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []
                hash_groups[file_hash].append(record)
        
        # Generate duplicate suggestions
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                # Keep the file with the shortest path, suggest others for removal
                files.sort(key=lambda x: len(x.get("path", "")))
                original = files[0]
                for duplicate in files[1:]:
                    suggestions.append({
                        "type": "duplicate",
                        "file": duplicate.get("filename", ""),
                        "suggestion": f"Duplicate of '{original.get('filename', '')}'. Consider removing.",
                        "original_path": original.get("path", ""),
                        "duplicate_path": duplicate.get("path", "")
                    })
        
        # Generate naming suggestions
        for record in current_index[:20]:  # Limit to first 20 for demo
            filename = record.get("filename", "")
            if any(pattern in filename.lower() for pattern in ["copy", "untitled", "img_", "dsc_"]):
                # Extract content-based name suggestion
                text_content = record.get("text_content", "")
                if text_content:
                    # Simple title extraction
                    lines = text_content.split('\n')
                    first_line = lines[0].strip() if lines else ""
                    if first_line and len(first_line) < 50:
                        suggested_name = first_line.replace(" ", "_")[:30] + os.path.splitext(filename)[1]
                        suggestions.append({
                            "type": "rename",
                            "file": filename,
                            "suggestion": f"Rename to '{suggested_name}' based on content",
                            "current_path": record.get("path", ""),
                            "suggested_name": suggested_name
                        })
        
        return {"suggestions": suggestions[:20]}  # Limit to 20 suggestions
        
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return {"suggestions": []}

@app.get("/api/status")
def get_status():
    """Returns the current status of the system."""
    try:
        stats = get_scan_status()
        
        status_info = {
            "status": "online", 
            "scan_paths": SCAN_PATHS,
            "total_files": stats.get("total_files", 0),
            "indexed_files": stats.get("indexed_files", 0),
            "file_types": stats.get("file_types", {}),
            "index_exists": os.path.exists("smartfolder_index.json"),
            "face_clusters": len(get_face_clusters_summary())
        }
        
        return status_info
        
    except Exception as e:
        print(f"Error getting status: {e}")
        return {
            "status": "error", 
            "scan_paths": SCAN_PATHS,
            "error": str(e)
        }

@app.get("/api/stats")
def get_detailed_stats():
    """Get detailed statistics about the indexed files."""
    global current_index
    
    try:
        if not current_index:
            current_index = load_index()
        
        if not current_index:
            return {"error": "No data available"}
        
        stats = {
            "total_files": len(current_index),
            "total_size": sum(record.get("size", 0) for record in current_index),
            "file_types": {},
            "indexed_files": 0,
            "files_with_text": 0,
            "files_with_faces": 0
        }
        
        for record in current_index:
            # File type distribution
            file_type = record.get("file_type", "unknown")
            stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1
            
            # Content analysis
            if record.get("indexed"):
                stats["indexed_files"] += 1
            if record.get("text_content"):
                stats["files_with_text"] += 1
            if record.get("faces_detected"):
                stats["files_with_faces"] += 1
        
        return stats
        
    except Exception as e:
        print(f"Error getting detailed stats: {e}")
        return {"error": str(e)}

@app.get("/api/file-thumbnail/{file_path:path}")
def get_file_thumbnail(file_path: str):
    """Generate and return a thumbnail for an image file."""
    try:
        # Security check - ensure file is within scan paths
        abs_file_path = os.path.abspath(file_path)
        allowed = False
        for scan_path in SCAN_PATHS:
            if abs_file_path.startswith(os.path.abspath(scan_path)):
                allowed = True
                break
        
        if not allowed:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not os.path.exists(abs_file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # For now, return the original file
        # In production, generate actual thumbnails
        return FileResponse(abs_file_path)
        
    except Exception as e:
        print(f"Error getting thumbnail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Initialize on startup ---
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global current_index
    
    print("Smart Folder Organizer starting up...")
    
    # Load existing index if available
    try:
        current_index = load_index()
        if current_index:
            print(f"Loaded existing index with {len(current_index)} files")
        else:
            print("No existing index found")
    except Exception as e:
        print(f"Error loading index: {e}")
    
    # Initialize vector database
    try:
        initialize_qdrant()
        print("Vector database initialized")
    except Exception as e:
        print(f"Warning: Vector database initialization failed: {e}")
    
    print("Smart Folder Organizer ready!")

# --- Serve Frontend Static Files ---
# The Dockerfile copies the built React app to /app/app/static
if os.path.exists("app/static"):
    app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
else:
    print("Warning: Frontend static files not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)