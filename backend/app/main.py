import base64
from pathlib import Path
from typing import List
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    EnrollmentRequest,
    VerificationRequest,
    SuccessResponse,
    ErrorResponse
)
from app.face_processor import FaceProcessor
from app.storage import EnrollmentStorage

# Initialize FastAPI app
app = FastAPI(
    title="Face Recognition MVP",
    description="Backend API for face enrollment and verification",
    version="1.0.0"
)

# Setup CORS middleware for localhost (any port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage (lightweight)
storage = EnrollmentStorage(storage_dir=Path("./face_data"))

# Lazy load face processor (to avoid blocking startup with model downloads)
_face_processor = None

def get_face_processor():
    """Lazy initialization of FaceProcessor"""
    global _face_processor
    if _face_processor is None:
        print("Initializing FaceProcessor (downloading models if needed)...")
        _face_processor = FaceProcessor()
        print("FaceProcessor ready.")
    return _face_processor


@app.on_event("startup")
async def startup_event():
    """Warm up models on startup"""
    print("Starting up Face Recognition MVP backend...")
    print("Startup complete. Ready to accept requests.")
    print("Note: DeepFace models will be downloaded on first use.")


@app.post("/enroll", response_model=SuccessResponse)
async def enroll(request: EnrollmentRequest):
    """
    Enroll a face using multiple frames
    
    Requires at least 5 frames with valid face detections
    """
    frames = request.frames
    
    # Require at least 5 frames
    if len(frames) < 5:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient frames: {len(frames)} provided, minimum 5 required"
        )
    
    valid_embeddings = []
    valid_metadata = []
    errors = []
    
    # Process each frame
    for idx, frame in enumerate(frames):
        try:
            # Decode base64 image (handle data URI format)
            image_str = frame.image
            if ',' in image_str:
                # Split on comma and take second part (after data:image/...;base64,)
                image_str = image_str.split(',')[1]
            
            image_data = base64.b64decode(image_str)
            
            # Process frame
            result = get_face_processor().process_frame(image_data, frame.pose)
            
            if result['error'] is not None:
                errors.append(f"Frame {idx + 1} ({frame.pose}): {result['error']}")
                continue
            
            if result['embedding'] is not None:
                valid_embeddings.append(result['embedding'])
                valid_metadata.append({
                    'pose': result['pose_label'],
                    'timestamp': result['timestamp'],
                    'confidence': result['confidence'],
                    'face_ratio': result['face_ratio']
                })
        
        except Exception as e:
            errors.append(f"Frame {idx + 1} ({frame.pose}): Processing error - {str(e)}")
            continue
    
    # Check if we have enough valid embeddings
    if len(valid_embeddings) < 5:
        error_msg = f"Insufficient valid embeddings: {len(valid_embeddings)} valid out of {len(frames)} frames"
        if errors:
            error_msg += f". Errors: {'; '.join(errors[:5])}"  # Show first 5 errors
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Save enrollment
    try:
        storage.save_enrollment(valid_embeddings, valid_metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save enrollment: {str(e)}")
    
    return SuccessResponse(
        message=f"Successfully enrolled {len(valid_embeddings)} face embeddings",
        data={
            "embeddings_count": len(valid_embeddings),
            "metadata": valid_metadata,
            "errors": errors if errors else None
        }
    )


@app.post("/verify", response_model=SuccessResponse)
async def verify(request: VerificationRequest):
    """
    Verify if an image matches the enrolled face
    """
    # Check if enrollment exists
    if not storage.is_enrolled():
        raise HTTPException(
            status_code=400,
            detail="No enrollment found. Please enroll a face first."
        )
    
    try:
        # Decode base64 image
        image_str = request.image
        if ',' in image_str:
            image_str = image_str.split(',')[1]
        
        image_data = base64.b64decode(image_str)
        
        # Load stored embeddings
        stored_embeddings = storage.load_embeddings()
        if stored_embeddings is None:
            raise HTTPException(status_code=500, detail="Failed to load stored embeddings")
        
        # Verify face
        is_match, similarity, message = get_face_processor().verify_face(
            image_data,
            stored_embeddings,
            threshold=0.6
        )
        
        return SuccessResponse(
            message=message,
            data={
                "verified": is_match,
                "similarity": similarity,
                "threshold": 0.6
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")


@app.get("/status", response_model=SuccessResponse)
async def get_status():
    """
    Get enrollment status and number of embeddings
    """
    is_enrolled = storage.is_enrolled()
    
    data = {
        "enrolled": is_enrolled
    }
    
    if is_enrolled:
        embeddings = storage.load_embeddings()
        metadata = storage.load_metadata()
        
        if embeddings is not None:
            data["embeddings_count"] = len(embeddings)
        
        if metadata is not None:
            data["metadata"] = {
                "version": metadata.get("version"),
                "timestamp": metadata.get("timestamp"),
                "count": metadata.get("count")
            }
    
    return SuccessResponse(
        message="Status retrieved successfully",
        data=data
    )


@app.delete("/enrollment", response_model=SuccessResponse)
async def delete_enrollment():
    """
    Clear enrollment data
    """
    if not storage.is_enrolled():
        raise HTTPException(
            status_code=404,
            detail="No enrollment found to delete"
        )
    
    try:
        storage.clear_enrollment()
        return SuccessResponse(
            message="Enrollment data cleared successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear enrollment: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Face Recognition MVP API",
        "version": "1.0.0",
        "endpoints": {
            "enroll": "POST /enroll",
            "verify": "POST /verify",
            "status": "GET /status",
            "delete": "DELETE /enrollment"
        }
    }


@app.get("/health")
async def health_check():
    """
    Simple health check endpoint for Render
    Returns immediately without loading models
    """
    return {
        "status": "healthy",
        "service": "Face Recognition MVP",
        "version": "1.0.0"
    }
