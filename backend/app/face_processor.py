import cv2
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime
from deepface import DeepFace


class FaceProcessor:
    """Handles face detection, embedding extraction, and verification"""
    
    def __init__(self):
        """Initialize FaceProcessor with DeepFace configuration"""
        self.detector_backend = 'retinaface'
        self.model_name = 'Facenet512'
        self._warmup()
    
    def _warmup(self):
        """Pre-load models by running a dummy inference"""
        print("Warming up DeepFace models...")
        try:
            # Create a dummy image (200x200 RGB)
            dummy_image = np.ones((200, 200, 3), dtype=np.uint8) * 128
            # This will trigger model downloads and loading on first run
            # We expect this to fail (no face), but it will load the models
            try:
                DeepFace.represent(
                    dummy_image,
                    detector_backend=self.detector_backend,
                    model_name=self.model_name,
                    enforce_detection=True,
                    align=True
                )
            except Exception:
                # Expected to fail - no face in dummy image, but models are now loaded
                pass
            print("DeepFace models loaded successfully")
        except Exception as e:
            print(f"Warning: Model warmup encountered an issue: {e}")
            print("Models will be loaded on first actual inference")
    
    def process_frame(self, image_data: bytes, pose_label: str) -> Dict:
        """
        Process a single frame to extract face embedding
        
        Args:
            image_data: Raw image bytes
            pose_label: Label for the pose (e.g., 'front', 'left', 'right')
        
        Returns:
            Dict with keys: embedding, confidence, face_area, face_ratio, pose_label, timestamp, error
        """
        result = {
            'embedding': None,
            'confidence': None,
            'face_area': None,
            'face_ratio': None,
            'pose_label': pose_label,
            'timestamp': datetime.utcnow().isoformat(),
            'error': None
        }
        
        try:
            # Decode bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                result['error'] = "Failed to decode image"
                return result
            
            # Validate image size (at least 200x200)
            height, width = img.shape[:2]
            if height < 200 or width < 200:
                result['error'] = f"Image too small: {width}x{height}. Minimum 200x200 required"
                return result
            
            # Calculate image area
            image_area = width * height
            
            # Call DeepFace.represent
            try:
                deepface_result = DeepFace.represent(
                    img,
                    detector_backend=self.detector_backend,
                    model_name=self.model_name,
                    enforce_detection=True,
                    align=True
                )
            except Exception as e:
                result['error'] = f"DeepFace processing failed: {str(e)}"
                return result
            
            # Check exactly 1 face detected
            if not isinstance(deepface_result, list):
                result['error'] = "Unexpected DeepFace result format"
                return result
            
            if len(deepface_result) == 0:
                result['error'] = "No face detected in image"
                return result
            
            if len(deepface_result) > 1:
                result['error'] = f"Multiple faces detected ({len(deepface_result)}). Exactly 1 face required"
                return result
            
            # Extract embedding and facial area
            face_data = deepface_result[0]
            embedding = np.array(face_data['embedding'], dtype=np.float32)
            
            # Extract facial area
            facial_area = face_data.get('facial_area', {})
            x = facial_area.get('x', 0)
            y = facial_area.get('y', 0)
            w = facial_area.get('w', 0)
            h = facial_area.get('h', 0)
            
            face_area = w * h
            face_ratio = face_area / image_area if image_area > 0 else 0
            
            # Reject if face too small (face_ratio < 0.05)
            if face_ratio < 0.05:
                result['error'] = f"Face too small (ratio: {face_ratio:.4f}). Minimum 0.05 required"
                return result
            
            # Calculate confidence (using face_ratio as proxy, or use detection confidence if available)
            confidence = face_ratio  # Using face_ratio as confidence metric
            
            result['embedding'] = embedding
            result['confidence'] = float(confidence)
            result['face_area'] = int(face_area)
            result['face_ratio'] = float(face_ratio)
            result['error'] = None
            
        except Exception as e:
            result['error'] = f"Unexpected error processing frame: {str(e)}"
        
        return result
    
    def verify_face(
        self, 
        image_data: bytes, 
        stored_embeddings: np.ndarray, 
        threshold: float = 0.6
    ) -> Tuple[bool, float, str]:
        """
        Verify if an image matches stored embeddings
        
        Args:
            image_data: Raw image bytes to verify
            stored_embeddings: numpy array of shape (N, 512) with stored embeddings
            threshold: Cosine similarity threshold for match (default 0.6)
        
        Returns:
            Tuple of (is_match: bool, best_similarity: float, message: str)
        """
        try:
            # Process frame to get embedding
            result = self.process_frame(image_data, pose_label="verification")
            
            if result['error'] is not None:
                return False, 0.0, f"Face processing failed: {result['error']}"
            
            if result['embedding'] is None:
                return False, 0.0, "Failed to extract embedding"
            
            query_embedding = result['embedding']
            
            # Compute cosine similarity with all stored embeddings
            similarities = self._cosine_similarity(query_embedding, stored_embeddings)
            
            # Find best similarity
            best_similarity = float(np.max(similarities))
            
            # Check if match
            is_match = best_similarity >= threshold
            
            if is_match:
                message = f"Face verified with similarity: {best_similarity:.4f}"
            else:
                message = f"Face not verified. Best similarity: {best_similarity:.4f} (threshold: {threshold})"
            
            return is_match, best_similarity, message
            
        except Exception as e:
            return False, 0.0, f"Verification error: {str(e)}"
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Compute cosine similarity between vectors
        
        Args:
            a: Query vector of shape (512,)
            b: Stored embeddings of shape (N, 512) or single vector (512,)
        
        Returns:
            Array of similarities of shape (N,) or scalar if b is single vector
        """
        # Normalize vectors
        a_norm = a / (np.linalg.norm(a) + 1e-8)
        
        if b.ndim == 1:
            # Single vector case
            b_norm = b / (np.linalg.norm(b) + 1e-8)
            similarity = np.dot(a_norm, b_norm)
            return similarity
        else:
            # Matrix case: (N, 512)
            b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-8)
            # Compute dot product for each row
            similarities = np.dot(b_norm, a_norm)
            return similarities
