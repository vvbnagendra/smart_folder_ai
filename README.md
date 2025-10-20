# Smart Folder Organizer and Search Assistant

This project implements a cross-platform "Smart Folder Organizer and Search Assistant" as a single Docker container solution. It provides comprehensive file indexing, OCR, face detection, semantic search, and a web-based dashboard.

## Architecture & Tech Stack

- **Backend**: Python (FastAPI)
- **Frontend**: React + Tailwind + shaden UI
- **Database/Indexing**: PostgreSQL (metadata - optional), Qdrant (vector search - optional)
- **AI/OCR**: Tesseract/PaddleOCR, CLIP/OpenAI Embeddings, `face_recognition`/`DeepFace`

## Requirements

The application runs in a single Docker container and exposes a web interface on port 8080. It mounts a local folder (`/my/folders` in the example) to the container's internal data path (`/data`) for scanning.

### How to run with Docker

1.  **Build the Docker image:**
    ```bash
    docker build -t smartfolder .
    ```

2.  **Run the container:**
    Replace `/path/to/your/local/folders` with the absolute path to the directory you want to scan.
    ```bash
    docker run -d -p 8080:8080 -v /path/to/your/local/folders:/data --name smartfolder_app smartfolder
    ```
    The application will be accessible at `http://localhost:8080`.

3.  **Configure Scan Paths (Optional):**
    You can create a `.env` file based on `sample.env` to configure multiple scan paths, database connections, or API keys.

    ```bash
    # Example .env file content:
    # SCAN_PATHS="/data/documents:/data/photos"
    # OPENAI_API_KEY="sk-..."
    
    # Run with custom configuration:
    docker run -d -p 8080:8080 -v /path/to/your/local/folders:/data --env-file .env --name smartfolder_app smartfolder
    ```

## Example Queries

The web dashboard provides a search bar to query your indexed content.

| Feature | Query Example | Description |
| :--- | :--- | :--- |
| **Keyword Search** | `project scope 2025` | Finds files where the filename, path, or OCR'd content contains these words. |
| **Semantic Search** | `files about the new marketing strategy` | Finds files that are conceptually similar to the query, even if the exact words are not present. |
| **Face Search** | Click on a face cluster (e.g., "John Doe") | Shows all photos and videos where that person appears. |

## Folder Structure Visualization

The dashboard includes a visual folder map (tree view) and analytics view showing:
- File distribution by type (documents, images, videos)
- Summary of detected duplicates (by hash and semantic similarity)
- Summary of detected face clusters

---
*This is a minimal but functional implementation. Core components are stubbed out in `app/main.py` and will be expanded in `app/scanner.py`, `app/ocr_engine.py`, and `app/face_cluster.py`.*

