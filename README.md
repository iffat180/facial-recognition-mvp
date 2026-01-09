# Face Recognition MVP - Phase 1: Backend Foundation

A FastAPI-based backend for face recognition using DeepFace with RetinaFace detector and Facenet512 model.

## Project Structure

```
face-recognition-mvp/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application and endpoints
│   │   ├── face_processor.py # Face detection and verification logic
│   │   ├── storage.py       # Enrollment data persistence
│   │   └── models.py        # Pydantic request/response models
│   ├── face_data/           # Storage directory for embeddings
│   │   └── .gitkeep
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
└── README.md
```

## Features

- **Face Enrollment**: Enroll a face using multiple frames (minimum 5) with different poses
- **Face Verification**: Verify if an image matches the enrolled face
- **Status Check**: Check enrollment status and metadata
- **Enrollment Management**: Clear enrollment data

## Setup

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Run the server**:
```bash
uvicorn app.main:app --reload
```

The server will start on `http://localhost:8000` by default.

**Note**: On first run, DeepFace will download the RetinaFace detector and Facenet512 model. This may take a few minutes.

## API Endpoints

### POST `/enroll`
Enroll a face using multiple frames.

**Request Body**:
```json
{
  "frames": [
    {
      "pose": "front",
      "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
    },
    {
      "pose": "left",
      "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
    }
    // ... at least 5 frames required
  ]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Successfully enrolled 5 face embeddings",
  "data": {
    "embeddings_count": 5,
    "metadata": [...]
  }
}
```

### POST `/verify`
Verify if an image matches the enrolled face.

**Request Body**:
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response**:
```json
{
  "success": true,
  "message": "Face verified with similarity: 0.8234",
  "data": {
    "verified": true,
    "similarity": 0.8234,
    "threshold": 0.6
  }
}
```

### GET `/status`
Get enrollment status and metadata.

**Response**:
```json
{
  "success": true,
  "message": "Status retrieved successfully",
  "data": {
    "enrolled": true,
    "embeddings_count": 5,
    "metadata": {
      "version": "1.0",
      "timestamp": "2024-01-01T12:00:00",
      "count": 5
    }
  }
}
```

### DELETE `/enrollment`
Clear all enrollment data.

**Response**:
```json
{
  "success": true,
  "message": "Enrollment data cleared successfully"
}
```

## Technical Details

- **Detector**: RetinaFace
- **Model**: Facenet512 (512-dimensional embeddings)
- **Similarity Metric**: Cosine similarity
- **Verification Threshold**: 0.6 (configurable)
- **Minimum Image Size**: 200x200 pixels
- **Minimum Face Ratio**: 5% of image area

## Error Handling

The API returns appropriate HTTP status codes:
- `400`: Bad request (invalid input, insufficient frames, etc.)
- `404`: Resource not found
- `500`: Internal server error

All errors include descriptive messages in the response body.

## CORS

The API is configured to allow requests from `http://localhost:3000` for frontend development.

## Development

To run with auto-reload:
```bash
uvicorn app.main:app --reload
```

To run on a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

## Notes

- Models are pre-loaded on startup for faster first inference
- DeepFace will download models on first use (one-time download)
- All timestamps are in UTC ISO format
- Embeddings are stored as compressed numpy arrays (.npz format)
