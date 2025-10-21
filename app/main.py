import os
import platform
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from .scanner import scan_directory, load_index, search_files
from .indexer import initialize_qdrant, index_file_record, search_qdrant
from .face_cluster import get_face_clusters_summary, get_images_for_cluster
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv(dotenv_path="sample.env")

app = FastAPI(title="Smart Folder Organizer API")

# --- Configuration ---
# Default scan paths based on OS
def get_default_scan_paths():
    if platform.system() == "Windows":
        return [
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Pictures")
        ]
    elif platform.system() == "Darwin":  # macOS
        return [
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Pictures")
        ]
    else:  # Linux/Unix
        return ["/data"]

# Global state
current_index = []
current_scan_paths = get_default_scan_paths()

# --- Request Models ---
class SearchRequest(BaseModel):
    query: str
    search_type: str = "keyword"  # keyword or semantic

class ScanRequest(BaseModel):
    paths: List[str]

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

def validate_paths(paths: List[str]) -> List[str]:
    """Validate and filter valid directory paths."""
    valid_paths = []
    for path in paths:
        if os.path.isdir(path) and os.access(path, os.R_OK):
            valid_paths.append(os.path.abspath(path))
    return valid_paths

# --- API Endpoints ---

@app.get("/api/default-paths")
def get_default_paths():
    """Get suggested default scan paths based on the operating system."""
    paths = get_default_scan_paths()
    # Check which paths actually exist and are accessible
    available_paths = []
    for path in paths:
        if os.path.exists(path) and os.access(path, os.R_OK):
            available_paths.append({
                "path": path,
                "exists": True,
                "readable": True,
                "size_estimate": get_directory_size_estimate(path)
            })
        else:
            available_paths.append({
                "path": path,
                "exists": os.path.exists(path),
                "readable": False,
                "size_estimate": 0
            })
    
    return {
        "default_paths": available_paths,
        "os": platform.system(),
        "common_folders": get_common_folders()
    }

def get_common_folders():
    """Get common folders that users might want to scan."""
    common = []
    if platform.system() == "Windows":
        # Windows common folders
        possible_paths = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Pictures"),
            os.path.expanduser("~/Videos"),
            os.path.expanduser("~/Music"),
            "C:/Users/Public/Documents",
            "C:/Users/Public/Pictures"
        ]
    elif platform.system() == "Darwin":  # macOS
        possible_paths = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Pictures"),
            os.path.expanduser("~/Movies"),
            os.path.expanduser("~/Music")
        ]
    else:  # Linux
        possible_paths = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Pictures"),
            os.path.expanduser("~/Videos"),
            os.path.expanduser("~/Music"),
            "/home",
            "/mnt",
            "/media"
        ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.R_OK):
            common.append(path)
    
    return common

def get_directory_size_estimate(path: str) -> int:
    """Get a rough estimate of directory size (first 1000 files)."""
    try:
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                if file_count >= 1000:  # Limit for performance
                    break
                try:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except (OSError, IOError):
                    continue
            if file_count >= 1000:
                break
        return total_size
    except:
        return 0

@app.post("/api/scan")
def scan_folders(request: Optional[ScanRequest] = None):
    """Starts the recursive folder scan and indexing process."""
    global current_index, current_scan_paths
    
    # Use provided paths or current scan paths
    if request and request.paths:
        scan_paths = validate_paths(request.paths)
        current_scan_paths = scan_paths
    else:
        scan_paths = validate_paths(current_scan_paths)
    
    if not scan_paths:
        raise HTTPException(status_code=400, detail="No valid scan paths provided or found")
    
    try:
        print(f"Starting scan of paths: {scan_paths}")
        
        # Perform the scan
        file_records = scan_directory(scan_paths)
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
            "scan_paths": scan_paths
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

@app.get("/api/status")
def get_status():
    """Returns the current status of the system."""
    try:
        stats = get_scan_status()
        
        status_info = {
            "status": "online", 
            "scan_paths": current_scan_paths,
            "total_files": stats.get("total_files", 0),
            "indexed_files": stats.get("indexed_files", 0),
            "file_types": stats.get("file_types", {}),
            "index_exists": os.path.exists("smartfolder_index.json"),
            "face_clusters": len(get_face_clusters_summary()),
            "os": platform.system()
        }
        
        return status_info
        
    except Exception as e:
        print(f"Error getting status: {e}")
        return {
            "status": "error", 
            "scan_paths": current_scan_paths,
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

# --- Initialize on startup ---
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global current_index
    
    print("Smart Folder Organizer starting up...")
    print(f"Operating System: {platform.system()}")
    print(f"Default scan paths: {current_scan_paths}")
    
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