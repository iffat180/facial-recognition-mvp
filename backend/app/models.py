from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class FrameData(BaseModel):
    """Single frame data with pose label and base64 image"""
    pose: str = Field(..., description="Pose label (e.g., 'front', 'left', 'right')")
    image: str = Field(..., description="Base64 encoded image (with or without data URI prefix)")


class EnrollmentRequest(BaseModel):
    """Request model for face enrollment"""
    frames: List[FrameData] = Field(..., min_items=1, description="List of frames with pose labels and images")


class VerificationRequest(BaseModel):
    """Request model for face verification"""
    image: str = Field(..., description="Base64 encoded image (with or without data URI prefix)")


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[Dict] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    details: Optional[Dict] = None
