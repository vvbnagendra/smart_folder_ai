import os
import hashlib
import json
from typing import List, Dict, Any, Optional
from .ocr_engine import ocr_file
from .face_cluster import detect_and_encode_faces, cluster_faces

# Enhanced index structure
INDEX_FILE = "smartfolder_index.json"
SEARCH_INDEX = {}  # In-memory search index for better performance

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

def is_image_file(filepath: str) -> bool:
    """Check if file is an image based on extension."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    return os.path.splitext(filepath)[1].lower() in image_extensions

def is_text_file(filepath: str) -> bool:
    """Check if file is a text file based on extension."""
    text_extensions = {'.txt', '.md', '.csv', '.json', '.xml', '.log', '.py', '.js', '.html', '.css'}
    return os.path.splitext(filepath)[1].lower() in text_extensions

def extract_text_content(filepath: str) -> str:
    """Extract text content from various file types."""
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    # Try OCR for images and PDFs
    if ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.pdf']:
        return ocr_file(filepath)
    
    # Direct text extraction for text files
    elif is_text_file(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # First 1000 chars
                return content
        except Exception as e:
            print(f"Error reading text file {filepath}: {e}")
            return ""
    
    return ""

def generate_embeddings(text: str) -> List[float]:
    """Generate embedding vector for text content."""
    # Simplified embedding generation - in a real app, use sentence-transformers or OpenAI
    if not text:
        return [0.0] * 384  # Return zero vector for empty text
    
    # Simple hash-based embedding for demo purposes
    # In production, use actual embedding models
    import hashlib
    text_hash = hashlib.md5(text.lower().encode()).hexdigest()
    
    # Convert hash to numeric vector
    embedding = []
    for i in range(0, len(text_hash), 2):
        hex_pair = text_hash[i:i+2]
        embedding.append(int(hex_pair, 16) / 255.0)  # Normalize to 0-1
    
    # Pad or truncate to desired dimension
    while len(embedding) < 384:
        embedding.extend(embedding[:384-len(embedding)])
    
    return embedding[:384]

def process_file_content(filepath: str) -> Dict[str, Any]:
    """Enhanced content processing with better search indexing."""
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    content_data = {
        "text_content": "",
        "embedding_vector": None,
        "faces_detected": [],
        "file_type": "unknown"
    }
    
    # Extract text content
    text_content = extract_text_content(filepath)
    content_data["text_content"] = text_content
    
    # Generate embeddings if we have text content
    if text_content:
        content_data["embedding_vector"] = generate_embeddings(text_content)
    
    # Process images for face detection
    if is_image_file(filepath):
        content_data["file_type"] = "image"
        faces_data = detect_and_encode_faces(filepath)
        if faces_data:
            cluster_ids = cluster_faces(faces_data)
            content_data["faces_detected"] = cluster_ids
    elif ext == '.pdf':
        content_data["file_type"] = "document"
    elif is_text_file(filepath):
        content_data["file_type"] = "text"
    elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
        content_data["file_type"] = "video"
    elif ext in ['.mp3', '.wav', '.flac', '.aac']:
        content_data["file_type"] = "audio"
    
    return content_data

def build_search_index(records: List[Dict[str, Any]]):
    """Build an in-memory search index for faster searching."""
    global SEARCH_INDEX
    SEARCH_INDEX = {
        'by_filename': {},
        'by_content': {},
        'by_path': {},
        'by_type': {},
        'all_records': records
    }
    
    for i, record in enumerate(records):
        filename = record.get('filename', '').lower()
        content = record.get('text_content', '').lower()
        path = record.get('path', '').lower()
        file_type = record.get('file_type', 'unknown')
        
        # Index by filename words
        for word in filename.split():
            if word not in SEARCH_INDEX['by_filename']:
                SEARCH_INDEX['by_filename'][word] = []
            SEARCH_INDEX['by_filename'][word].append(i)
        
        # Index by content words
        for word in content.split():
            if len(word) > 2:  # Skip very short words
                if word not in SEARCH_INDEX['by_content']:
                    SEARCH_INDEX['by_content'][word] = []
                SEARCH_INDEX['by_content'][word].append(i)
        
        # Index by path components
        for word in path.replace('/', ' ').split():
            if word not in SEARCH_INDEX['by_path']:
                SEARCH_INDEX['by_path'][word] = []
            SEARCH_INDEX['by_path'][word].append(i)
        
        # Index by file type
        if file_type not in SEARCH_INDEX['by_type']:
            SEARCH_INDEX['by_type'][file_type] = []
        SEARCH_INDEX['by_type'][file_type].append(i)

def scan_directory(scan_paths: List[str]) -> List[Dict[str, Any]]:
    """Enhanced directory scanning with better error handling and progress tracking."""
    index_data = []
    total_files = 0
    processed_files = 0
    
    # Count total files first
    for root_path in scan_paths:
        if not os.path.isdir(root_path):
            print(f"Warning: Scan path not found: {root_path}")
            continue
        
        for root, _, files in os.walk(root_path):
            total_files += len([f for f in files if f != INDEX_FILE])
    
    print(f"Found {total_files} files to process")
    
    for root_path in scan_paths:
        if not os.path.isdir(root_path):
            continue

        print(f"Scanning directory: {root_path}")
        
        for root, _, files in os.walk(root_path):
            for file in files:
                if file == INDEX_FILE:
                    continue
                
                processed_files += 1
                filepath = os.path.join(root, file)
                
                # Progress indicator
                if processed_files % 50 == 0:
                    print(f"Progress: {processed_files}/{total_files} files processed")
                
                try:
                    # Collect basic metadata
                    stat = os.stat(filepath)
                    
                    file_record = {
                        "path": filepath,
                        "filename": file,
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                        "hash": "",
                        "indexed": False,
                        "file_type": "unknown",
                        "text_content": "",
                        "embedding_vector": None,
                        "faces_detected": []
                    }
                    
                    # Only process non-empty files
                    if file_record["size"] > 0:
                        try:
                            file_record["hash"] = calculate_hash(filepath)
                            if file_record["hash"]:
                                content_data = process_file_content(filepath)
                                file_record.update(content_data)
                                file_record["indexed"] = True
                        except Exception as e:
                            print(f"Error processing {filepath}: {e}")
                    
                    index_data.append(file_record)
                    
                except Exception as e:
                    print(f"Error accessing {filepath}: {e}")
                    continue
    
    print(f"Completed scanning. Processed {processed_files} files.")
    
    # Build search index
    build_search_index(index_data)
    
    return index_data

def save_index(data: List[Dict[str, Any]]):
    """Saves the index data to a JSON file with better error handling."""
    try:
        # Convert numpy arrays to lists for JSON serialization
        serializable_data = []
        for record in data:
            record_copy = record.copy()
            if record_copy.get("embedding_vector"):
                record_copy["embedding_vector"] = list(record_copy["embedding_vector"])
            serializable_data.append(record_copy)
        
        with open(INDEX_FILE, 'w') as f:
            json.dump(serializable_data, f, indent=2)
        print(f"Index saved to {INDEX_FILE}")
        
        # Also save a summary
        summary = {
            "total_files": len(data),
            "indexed_files": len([r for r in data if r.get("indexed", False)]),
            "file_types": {}
        }
        
        for record in data:
            file_type = record.get("file_type", "unknown")
            summary["file_types"][file_type] = summary["file_types"].get(file_type, 0) + 1
        
        with open("scan_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
    except Exception as e:
        print(f"Error saving index: {e}")

def load_index() -> List[Dict[str, Any]]:
    """Loads the index data from a JSON file and rebuilds search index."""
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r') as f:
                data = json.load(f)
                
            # Rebuild search index
            build_search_index(data)
            return data
        except Exception as e:
            print(f"Error loading index: {e}")
    return []

def search_files(query: str, search_type: str = "keyword") -> List[Dict[str, Any]]:
    """Enhanced search function with better matching."""
    if not SEARCH_INDEX:
        print("Search index not loaded")
        return []
    
    query_lower = query.lower()
    matching_indices = set()
    
    if search_type == "keyword":
        # Search in filename, content, and path
        query_words = query_lower.split()
        
        for word in query_words:
            # Exact word matches
            matching_indices.update(SEARCH_INDEX['by_filename'].get(word, []))
            matching_indices.update(SEARCH_INDEX['by_content'].get(word, []))
            matching_indices.update(SEARCH_INDEX['by_path'].get(word, []))
            
            # Partial matches
            for indexed_word in SEARCH_INDEX['by_filename']:
                if word in indexed_word or indexed_word in word:
                    matching_indices.update(SEARCH_INDEX['by_filename'][indexed_word])
            
            for indexed_word in SEARCH_INDEX['by_content']:
                if word in indexed_word or indexed_word in word:
                    matching_indices.update(SEARCH_INDEX['by_content'][indexed_word])
    
    elif search_type == "semantic":
        # For semantic search, we'd use actual embeddings
        # For now, implement as enhanced keyword search
        query_embedding = generate_embeddings(query)
        
        # Calculate similarity with all indexed documents
        scored_results = []
        for i, record in enumerate(SEARCH_INDEX['all_records']):
            if record.get('embedding_vector'):
                # Calculate cosine similarity (simplified)
                doc_embedding = record['embedding_vector']
                similarity = sum(a * b for a, b in zip(query_embedding, doc_embedding))
                if similarity > 0.1:  # Threshold
                    scored_results.append((i, similarity))
        
        # Sort by similarity
        scored_results.sort(key=lambda x: x[1], reverse=True)
        matching_indices = [i for i, _ in scored_results[:20]]  # Top 20 results
    
    # Return matching records
    results = []
    for i in matching_indices:
        if i < len(SEARCH_INDEX['all_records']):
            record = SEARCH_INDEX['all_records'][i].copy()
            # Add relevance score for display
            record['relevance'] = 1.0  # Simplified scoring
            results.append(record)
    
    return results[:50]  # Limit to 50 results

if __name__ == "__main__":
    # Example usage
    scan_paths = ["/data"]
    
    if not os.path.exists("/data"):
        print("Creating test data directory...")
        os.makedirs("/data", exist_ok=True)
        
        # Create some test files
        with open("/data/test_document.txt", "w") as f:
            f.write("This is a test document about machine learning and artificial intelligence.")
        
        with open("/data/meeting_notes.md", "w") as f:
            f.write("# Meeting Notes\n\nDiscussed the new project requirements and timeline.")
        
        print("Test files created.")
    
    print("Starting enhanced scan...")
    index = scan_directory(scan_paths)
    save_index(index)
    
    # Test search
    print("\nTesting search functionality...")
    results = search_files("machine learning", "keyword")
    print(f"Found {len(results)} results for 'machine learning'")
    
    for result in results[:3]:
        print(f"- {result['filename']}: {result.get('text_content', '')[:100]}...")