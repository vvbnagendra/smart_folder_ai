# Smart Folder Organizer with UI-Based Folder Selection

An enhanced cross-platform Smart Folder Organizer that allows you to select folders through a user-friendly web interface instead of configuration files. Perfect for Windows, macOS, and Linux users.

## 🚀 Key Features

- **UI-Based Folder Selection**: Choose folders to scan through the web interface
- **Cross-Platform Support**: Works on Windows, macOS, and Linux with proper path handling
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
- Docker and Docker Compose (recommended)
- OR Python 3.9+ and Node.js 18+ for local development
- At least 2GB RAM for optimal performance

### Option 1: Docker Setup (Recommended)

#### 1. Build the Docker Image
```bash
# Clone or download the project files
# Navigate to the project directory
docker build -t smartfolder .
```

#### 2. Run with Your Folders (Windows Examples)
```bash
# For Windows - scan your Documents and Downloads
docker run -d -p 8080:8080 \
  -v "C:\Users\%USERNAME%\Documents:/data/documents" \
  -v "C:\Users\%USERNAME%\Downloads:/data/downloads" \
  -v "C:\Users\%USERNAME%\Pictures:/data/pictures" \
  --name smartfolder_app smartfolder

# Alternative Windows PowerShell syntax
docker run -d -p 8080:8080 `
  -v "C:\Users\$env:USERNAME\Documents:/data/documents" `
  -v "C:\Users\$env:USERNAME\Downloads:/data/downloads" `
  -v "C:\Users\$env:USERNAME\Pictures:/data/pictures" `
  --name smartfolder_app smartfolder
```

#### 3. Run with Your Folders (macOS/Linux Examples)
```bash
# For macOS/Linux
docker run -d -p 8080:8080 \
  -v "$HOME/Documents:/data/documents" \
  -v "$HOME/Downloads:/data/downloads" \
  -v "$HOME/Pictures:/data/pictures" \
  --name smartfolder_app smartfolder
```

### Option 2: Local Development Setup

#### 1. Backend Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

#### 2. Frontend Setup (separate terminal)
```bash
cd frontend
npm install
npm run dev
```

### 3. Access the Application
Open your browser and navigate to: `http://localhost:8080`

## 📂 Folder Structure Examples

### Windows Folder Examples
The application will automatically suggest common Windows folders:

**Personal Folders:**
- `C:\Users\YourName\Documents`
- `C:\Users\YourName\Downloads`
- `C:\Users\YourName\Pictures`
- `C:\Users\YourName\Desktop`
- `C:\Users\YourName\Videos`
- `C:\Users\YourName\Music`

**Work/Project Folders:**
- `D:\Projects\MyWork`
- `C:\Work\Documents`
- `E:\BackupFiles`

**External Drives:**
- `D:\` (additional hard drive)
- `E:\` (external USB drive)
- `F:\USB_Backup`

### macOS Folder Examples
**Personal Folders:**
- `/Users/YourName/Documents`
- `/Users/YourName/Downloads`
- `/Users/YourName/Pictures`
- `/Users/YourName/Desktop`
- `/Users/YourName/Movies`

**External/Network:**
- `/Volumes/ExternalDrive`
- `/Volumes/NetworkShare`

### Linux Folder Examples
**Personal Folders:**
- `/home/username/Documents`
- `/home/username/Downloads`
- `/home/username/Pictures`

**System/External:**
- `/media/username/USB_Drive`
- `/mnt/external_drive`

## 📖 Usage Guide

### 1. Select Folders to Scan

1. **Access the Web Interface**: Open `http://localhost:8080`
2. **Click "Manage Folders"**: Expand the folder selection interface
3. **Choose Suggested Folders**: Click on checkboxes next to recommended folders
4. **Add Custom Folders**: Use the custom path input for specific directories
5. **Start Scan**: Click "Start Scan" to begin indexing

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

## 🔧 Configuration

### Environment Variables
Create a `.env` file for advanced configuration:

```bash
# Model to use for embeddings
EMBEDDING_MODEL="all-MiniLM-L6-v2"

# Optional: OpenAI API key for advanced embeddings
OPENAI_API_KEY="sk-your-api-key-here"

# Optional: External Qdrant instance
QDRANT_URL="http://localhost:6333"

# Log level
LOG_LEVEL="INFO"
```

### Windows-Specific Tips

1. **Path Format**: Use forward slashes `/` or double backslashes `\\` in paths
2. **Permissions**: Run as administrator if scanning system folders
3. **Antivirus**: Add the application to antivirus exceptions for better performance
4. **File Paths**: The application handles Windows path formats automatically

### Performance Optimization
- **File Limits**: Files larger than 100MB are skipped for performance
- **Batch Processing**: Files are processed in optimized batches
- **Memory Management**: Efficient indexing with memory-conscious algorithms
- **Skip Hidden Files**: Hidden and system files are automatically excluded

## 🐛 Troubleshooting

### Common Issues

#### "No valid scan paths provided or found"
1. **Check Folder Permissions**: Ensure the application can read the selected folders
2. **Verify Folder Exists**: Make sure the folders exist and are accessible
3. **Try Different Folders**: Start with a simple folder like Documents

#### "No results found" after scanning
1. **Check Scan Status**: Verify the scan completed successfully
2. **Try Different Search Terms**: Use broader keywords
3. **Switch Search Modes**: Try both keyword and semantic search

#### Windows Path Issues
1. **Use Full Paths**: Always use complete paths like `C:\Users\YourName\Documents`
2. **Avoid Spaces**: If issues with spaces, try folders without spaces first
3. **Check Permissions**: Some Windows folders require elevated permissions

#### Performance Issues
1. **Reduce Scan Scope**: Start with smaller folders
2. **Close Other Applications**: Free up memory and CPU
3. **Use SSD Storage**: Better I/O performance for faster scanning

### Debugging Commands

#### Docker Debugging
```bash
# Check application logs
docker logs smartfolder_app

# Access container shell
docker exec -it smartfolder_app /bin/bash

# Check container resources
docker stats smartfolder_app

# Restart application
docker restart smartfolder_app
```

#### Local Debugging
```bash
# Check Python logs
python -m app.main

# Test folder access
python -c "import os; print(os.listdir('C:/Users/YourName/Documents'))"
```

## 🔧 Development

### Adding New Features
The application is designed for extensibility:

- **New File Types**: Add processors to `scanner.py`
- **Enhanced OCR**: Integrate Tesseract or cloud OCR services
- **Real Face Recognition**: Add face_recognition library
- **Advanced Search**: Implement transformer-based embeddings

### Testing with Sample Data

Create a test folder structure:

#### Windows Test Structure:
```
C:\TestData\
├── Documents\
│   ├── report.pdf
│   ├── meeting_notes.txt
│   └── project_plan.docx
├── Images\
│   ├── family_photo.jpg
│   ├── vacation_pic.png
│   └── screenshot.png
└── Downloads\
    ├── invoice.pdf
    └── readme.txt
```

#### Create Test Files:
```powershell
# Windows PowerShell
mkdir C:\TestData\Documents, C:\TestData\Images, C:\TestData\Downloads
echo "This is a test document about machine learning." > C:\TestData\Documents\test_doc.txt
echo "Meeting notes from today's discussion." > C:\TestData\Documents\notes.txt
```

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, or Ubuntu 18.04
- **CPU**: 2 cores
- **RAM**: 2GB
- **Storage**: 1GB + space for your files
- **Docker**: Version 20.10+ (if using Docker)

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

### Windows Users Quick Start Checklist:

✅ Install Docker Desktop  
✅ Open PowerShell as Administrator  
✅ Run the Docker command with your actual username  
✅ Open `http://localhost:8080`  
✅ Select folders using the web interface  
✅ Click "Start Scan"  
✅ Start searching your files!  

**Example for Windows:**
Replace `YourName` with your actual Windows username in paths like `C:\Users\YourName\Documents`