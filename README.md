# Smart Folder Organizer and Search Assistant

An enhanced cross-platform "Smart Folder Organizer and Search Assistant" implemented as a single Docker container solution. This application provides comprehensive file indexing, OCR, face detection, semantic search, and a modern web-based dashboard.

## 🚀 Key Features

- **Advanced File Indexing**: Scans and indexes files with metadata extraction
- **OCR Technology**: Extracts text from images and PDFs
- **Face Recognition**: Detects and clusters faces in photos with thumbnail previews
- **Dual Search Modes**: 
  - Keyword search for exact matches
  - Semantic search for conceptual similarity
- **Modern Web Interface**: React-based dashboard with real-time updates
- **File Organization**: Smart suggestions for cleanup and renaming
- **Thumbnail Generation**: Visual previews for face clusters and images

## 🛠 Architecture & Tech Stack

- **Backend**: Python (FastAPI) with async support
- **Frontend**: React + Tailwind CSS + Modern UI components
- **Search Engine**: Qdrant (vector database) + custom indexing
- **AI/ML**: Scikit-learn, Pillow for image processing
- **OCR**: Enhanced text extraction with context-aware output
- **Face Detection**: Clustering algorithm with similarity matching

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- At least 2GB RAM for optimal performance
- Local folder with files to scan

### 1. Build the Docker Image
```bash
docker build -t smartfolder .
```

### 2. Run the Container
Replace `/path/to/your/local/folders` with the absolute path to the directory you want to scan:

```bash
# Basic usage
docker run -d -p 8080:8080 -v /path/to/your/local/folders:/data --name smartfolder_app smartfolder

# With custom configuration
docker run -d -p 8080:8080 \
  -v /path/to/your/local/folders:/data \
  -v /path/to/config:/app/config \
  --env-file .env \
  --name smartfolder_app smartfolder
```

### 3. Access the Application
Open your browser and navigate to: `http://localhost:8080`

## 🔧 Configuration

### Environment Variables
Create a `.env` file based on `sample.env`:

```bash
# Scan paths (colon-separated for multiple paths)
SCAN_PATHS="/data/documents:/data/photos:/data/downloads"

# Optional: OpenAI API key for advanced embeddings
OPENAI_API_KEY="sk-your-api-key-here"

# Embedding model (default uses local model)
EMBEDDING_MODEL="all-MiniLM-L6-v2"

# Optional: External Qdrant instance
QDRANT_URL="http://localhost:6333"
```

### Multiple Scan Paths
```bash
docker run -d -p 8080:8080 \
  -v /home/user/Documents:/data/documents \
  -v /home/user/Photos:/data/photos \
  -v /home/user/Downloads:/data/downloads \
  --name smartfolder_app smartfolder
```

## 📖 Usage Guide

### 1. Initial Setup
1. Start the application
2. Click **"Start Scan"** to index your files
3. Wait for the scan to complete (progress shown in real-time)

### 2. Search Features

#### Keyword Search
- **Purpose**: Find exact word matches in filenames and content
- **Example**: `"invoice 2024"` finds files containing both words
- **Best for**: Specific document names, dates, exact terms

#### Semantic Search  
- **Purpose**: Find conceptually related content
- **Example**: `"financial reports"` might find files about budgets, earnings, etc.
- **Best for**: Broad topic searches, concept-based discovery

#### Example Queries

| Search Type | Query | Finds |
|-------------|-------|-------|
| **Keyword** | `project scope 2024` | Files with all these words |
| **Keyword** | `meeting notes` | Files containing "meeting" and "notes" |
| **Semantic** | `vacation photos` | Images from trips, travel, holidays |
| **Semantic** | `work documents` | Business files, reports, presentations |

### 3. Face Recognition
- **Automatic Detection**: Faces are detected during scanning
- **Smart Clustering**: Similar faces are grouped together  
- **Visual Browsing**: Click on clusters to see all photos of that person
- **Thumbnail Previews**: Representative images for each cluster

### 4. File Organization
- **Duplicate Detection**: Identifies identical files by content hash
- **Smart Rename Suggestions**: Proposes better names based on content
- **File Type Analysis**: Shows distribution of document types

## 🎯 Advanced Features

### API Endpoints
The application exposes a REST API for programmatic access:

- `POST /api/scan` - Start file scanning
- `POST /api/search` - Perform searches  
- `GET /api/faces` - List face clusters
- `GET /api/status` - System status and statistics
- `GET /api/stats` - Detailed file statistics

### Performance Optimization
- **Incremental Scanning**: Only processes new/changed files
- **Efficient Indexing**: In-memory search index for fast queries
- **Thumbnail Caching**: Generated thumbnails are stored for quick access
- **Batch Processing**: Files are processed in optimized batches

### Security Considerations
- **Sandboxed Execution**: Runs as non-root user in container
- **Path Validation**: Prevents access outside mounted volumes
- **Input Sanitization**: All user inputs are validated and sanitized

## 🐛 Troubleshooting

### Common Issues

#### "No results found" after scanning
1. Check if files are actually in the mounted volume
2. Verify scan completed successfully (check status in UI)
3. Try different search terms or switch search modes

#### Face detection not working
1. Ensure you have image files (JPG, PNG, etc.)
2. Check that images contain clear, visible faces
3. Face detection is probabilistic - not all faces may be detected

#### Application won't start
1. Check Docker logs: `docker logs smartfolder_app`
2. Verify port 8080 is available
3. Ensure sufficient disk space and memory

#### Slow performance
1. Reduce scan scope to smaller directories
2. Increase Docker memory allocation
3. Use SSD storage for better I/O performance

### Debugging Commands
```bash
# Check application logs
docker logs smartfolder_app

# Access container shell
docker exec -it smartfolder_app /bin/bash

# Check system resources
docker stats smartfolder_app

# Restart application
docker restart smartfolder_app
```

## 🔧 Development

### Local Development Setup
```bash
# Clone and setup backend
cd app
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Setup frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Adding New Features
The application is designed for extensibility:

- **New file types**: Add processors to `scanner.py`
- **Enhanced OCR**: Integrate Tesseract or cloud OCR services
- **Real face recognition**: Add face_recognition library
- **Advanced search**: Implement transformer-based embeddings

## 📊 System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 2GB
- **Storage**: 1GB + space for your files
- **Docker**: Version 20.10+

### Recommended Requirements  
- **CPU**: 4+ cores
- **RAM**: 4GB+
- **Storage**: SSD recommended
- **Network**: For downloading models and updates

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details on:
- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions for questions and ideas

---

**Smart Folder Organizer** - Making file management intelligent and effortless! 🚀