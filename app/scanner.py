import os
import hashlib
import json
import platform
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

def normalize_path(path: str) -> str:
    """Normalize paths for cross-platform compatibility."""
    return os.path.normpath(os.path.abspath(path))

def is_image_file(filepath: str) -> bool:
    """Check if file is an image based on extension."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    return os.path.splitext(filepath)[1].lower() in image_extensions

def is_text_file(filepath: str) -> bool:
    """Check if file is a text file based on extension."""
    text_extensions = {'.txt', '.md', '.csv', '.json', '.xml', '.log', '.py', '.js', '.html', '.css', '.c', '.cpp', '.java'}
    return os.path.splitext(filepath)[1].lower() in text_extensions

def is_document_file(filepath: str) -> bool:
    """Check if file is a document based on extension."""
    doc_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.rtf', '.odt'}
    return os.path.splitext(filepath)[1].lower() in doc_extensions

def is_video_file(filepath: str) -> bool:
    """Check if file is a video based on extension."""
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
    return os.path.splitext(filepath)[1].lower() in video_extensions

def is_audio_file(filepath: str) -> bool:
    """Check if file is audio based on extension."""
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'}
    return os.path.splitext(filepath)[1].lower() in audio_extensions

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
            # Try different encodings for better compatibility
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read(2000)  # First 2000 chars
                        return content
                except UnicodeDecodeError:
                    continue
            return ""  # If all encodings fail
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

def determine_file_type(filepath: str) -> str:
    """Determine file type based on extension."""
    if is_image_file(filepath):
        return "image"
    elif is_document_file(filepath):
        return "document"
    elif is_text_file(filepath):
        return "text"
    elif is_video_file(filepath):
        return "video"
    elif is_audio_file(filepath):
        return "audio"
    else:
        return "unknown"

def process_file_content(filepath: str) -> Dict[str, Any]:
    """Enhanced content processing with better search indexing."""
    content_data = {
        "text_content": "",
        "embedding_vector": None,
        "faces_detected": [],
        "file_type": determine_file_type(filepath)
    }
    
    # Extract text content
    text_content = extract_text_content(filepath)
    content_data["text_content"] = text_content
    
    # Generate embeddings if we have text content
    if text_content:
        content_data["embedding_vector"] = generate_embeddings(text_content)
    
    # Process images for face detection
    if is_image_file(filepath):
        try:
            faces_data = detect_and_encode_faces(filepath)
            if faces_data:
                cluster_ids = cluster_faces(faces_data)
                content_data["faces_detected"] = cluster_ids
        except Exception as e:
            print(f"Error processing faces in {filepath}: {e}")
    
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
        for word in filename.replace('_', ' ').replace('-', ' ').split():
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
        path_normalized = path.replace('\\', '/').replace('_', ' ').replace('-', ' ')
        for word in path_normalized.split('/'):
            if word and len(word) > 2:
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
    
    print(f"OS Platform: {platform.system()}")
    print(f"Python version: {platform.python_version()}")
    
    # Normalize and validate paths
    valid_paths = []
    for path in scan_paths:
        normalized_path = normalize_path(path)
        if os.path.isdir(normalized_path):
            valid_paths.append(normalized_path)
            print(f"Valid scan path: {normalized_path}")
        else:
            print(f"Warning: Invalid or non-existent path: {path} (normalized: {normalized_path})")
    
    if not valid_paths:
        print("Error: No valid scan paths found!")
        return []
    
    # Count total files first
    for root_path in valid_paths:
        try:
            for root, dirs, files in os.walk(root_path):
                # Filter out hidden directories and system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in ['system volume information', '$recycle.bin', 'thumbs.db']]
                total_files += len([f for f in files if not f.startswith('.') and f != INDEX_FILE])
        except Exception as e:
            print(f"Error counting files in {root_path}: {e}")
    
    print(f"Found {total_files} files to process")
    
    for root_path in valid_paths:
        print(f"Scanning directory: {root_path}")
        
        try:
            for root, dirs, files in os.walk(root_path):
                # Filter out hidden and system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in ['system volume information', '$recycle.bin']]
                
                for file in files:
                    if file.startswith('.') or file == INDEX_FILE:
                        continue
                    
                    processed_files += 1
                    filepath = os.path.join(root, file)
                    
                    # Progress indicator
                    if processed_files % 100 == 0:
                        print(f"Progress: {processed_files}/{total_files} files processed ({(processed_files/total_files)*100:.1f}%)")
                    
                    try:
                        # Collect basic metadata
                        stat = os.stat(filepath)
                        
                        file_record = {
                            "path": normalize_path(filepath),
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
                        if file_record["size"] > 0 and file_record["size"] < 100 * 1024 * 1024:  # Skip files larger than 100MB
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
                        
        except Exception as e:
            print(f"Error walking directory {root_path}: {e}")
            continue
    
    print(f"Completed scanning. Processed {processed_files} files, indexed {len([r for r in index_data if r.get('indexed')])} files.")
    
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
        
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
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
        
        with open("scan_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
    except Exception as e:
        print(f"Error saving index: {e}")

def load_index() -> List[Dict[str, Any]]:
    """Loads the index data from a JSON file and rebuilds search index."""
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
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
        query_words = query_lower.replace('_', ' ').replace('-', ' ').split()
        
        for word in query_words:
            # Exact word matches
            matching_indices.update(SEARCH_INDEX['by_filename'].get(word, []))
            matching_indices.update(SEARCH_INDEX['by_content'].get(word, []))
            matching_indices.update(SEARCH_INDEX['by_path'].get(word, []))
            
            # Partial matches
            for indexed_word in list(SEARCH_INDEX['by_filename'].keys()) + list(SEARCH_INDEX['by_content'].keys()):
                if word in indexed_word or indexed_word in word:
                    if word in indexed_word:
                        matching_indices.update(SEARCH_INDEX['by_filename'].get(indexed_word, []))
                        matching_indices.update(SEARCH_INDEX['by_content'].get(indexed_word, []))
    
    elif search_type == "semantic":
        # For semantic search, we'd use actual embeddings
        # For now, implement as enhanced keyword search with similarity
        query_embedding = generate_embeddings(query)
        
        # Calculate similarity with all indexed documents
        scored_results = []
        for i, record in enumerate(SEARCH_INDEX['all_records']):
            if record.get('embedding_vector'):
                # Calculate cosine similarity (simplified)
                doc_embedding = record['embedding_vector']
                try:
                    similarity = sum(a * b for a, b in zip(query_embedding, doc_embedding))
                    similarity /= (sum(a * a for a in query_embedding) * sum(b * b for b in doc_embedding)) ** 0.5
                    if similarity > 0.1:  # Threshold
                        scored_results.append((i, similarity))
                except:
                    continue
        
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
    if platform.system() == "Windows":
        test_paths = [r"C:\Users\YourName\Documents"]  # Update with your actual path
    else:
        test_paths = ["/home/user/documents"]  # Update with your actual path
    
    print("Starting enhanced scan...")
    index = scan_directory(test_paths)
    save_index(index)
    
    # Test search
    print("\nTesting search functionality...")
    results = search_files("document", "keyword")
    print(f"Found {len(results)} results for 'document'")
    
    for result in results[:3]:
        print(f"- {result['filename']}: {result.get('text_content', '')[:100]}...")