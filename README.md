# Video Processing Backend Service

A Python backend service that accepts video file uploads, stores them locally, processes them through a neural network, and returns results to users asynchronously.

## Features

- **Video Upload**: Upload video files with automatic deduplication (SHA-256 hash)
- **Async Processing**: Long-running neural network processing in background
- **Real-time Updates**: WebSocket broadcast showing queue status to all connected clients
- **Polling API**: HTTP endpoints for checking task status and retrieving results
- **Auth Placeholder**: Designed for easy authentication integration later

## Quick Start

### Prerequisites

- Python 3.12+
- Conda (Miniconda or Anaconda)

### Installation

```bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate mousetrack
```

Alternatively, using pip with a virtual environment:

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://localhost:8000`.

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Upload Video
```
POST /api/v1/videos/upload
Content-Type: multipart/form-data

Form fields:
- video: File (video file)
- user_id: String (temporary, will be replaced by auth token)

Response:
{
    "task_id": "uuid",
    "status": "pending",
    "message": "Video uploaded successfully",
    "is_duplicate": false
}
```

### Get Task Status
```
GET /api/v1/tasks/{task_id}

Response:
{
    "task_id": "uuid",
    "status": "processing",
    "video_filename": "video.mp4",
    "progress": 50,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:01:00Z"
}
```

### Get Task Result
```
GET /api/v1/tasks/{task_id}/result

Response (completed):
{
    "task_id": "uuid",
    "status": "completed",
    "result": {...},
    "completed_at": "2024-01-01T00:05:00Z"
}
```

### WebSocket Queue Status
```
WebSocket /ws/queue

Connect to receive real-time updates about:
- NN processing status (busy/idle)
- Currently processing file name
- Queue of pending tasks
- Recently completed tasks
```

## Project Structure

```
mouseTrack-backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection and session management
│   ├── models/
│   │   ├── task.py             # Task model
│   │   └── user.py             # User model (placeholder for auth)
│   ├── schemas/
│   │   ├── task.py             # Pydantic schemas for tasks
│   │   └── user.py             # Pydantic schemas for users
│   ├── api/
│   │   ├── upload.py           # Upload endpoint
│   │   ├── tasks.py            # Task status and result endpoints
│   │   └── auth.py             # Auth endpoints (placeholder)
│   ├── services/
│   │   ├── upload_service.py   # File handling and deduplication
│   │   ├── task_service.py     # Task lifecycle management
│   │   ├── nn_processor.py     # Neural network processing (generic)
│   │   └── websocket_manager.py # WebSocket connection management and broadcast
│   └── utils/
│       └── file_utils.py       # File hashing and validation
├── videos/                     # Local video storage (auto-created)
├── .env                        # Environment variables
├── .env.example
├── requirements.txt
└── README.md
```

## Configuration

Environment variables (`.env`):

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Storage
VIDEO_STORAGE_PATH=./videos
MAX_FILE_SIZE_MB=500
ALLOWED_VIDEO_EXTENSIONS=mp4,avi,mov,mkv,webm

# Database
DATABASE_URL=sqlite:///./app.db

# Processing
NN_PROCESSING_TIMEOUT_SECONDS=3600
```

## Neural Network Integration

The neural network processor is located in [`app/services/nn_processor.py`](app/services/nn_processor.py:1). Replace the `DefaultNNProcessor` class with your actual implementation:

```python
class MyNNProcessor(NNProcessor):
    async def process(self, video_path: str) -> dict:
        # Your neural network processing logic here
        pass
```

Then update the global `processor` instance in the same file.

## Authentication Placeholder

The authentication system is designed to be added later:

1. **Current**: `user_id` passed as a form field in upload requests
2. **Future**: JWT token in Authorization header, `user_id` extracted from token
3. **Middleware**: Auth middleware will be added to intercept requests
4. **Database**: User model already exists for future expansion

## License

MIT
