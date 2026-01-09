import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class EnrollmentStorage:
    """Handles persistence of face embeddings and metadata"""
    
    def __init__(self, storage_dir: Path):
        """
        Initialize storage with directory path
        
        Args:
            storage_dir: Path to directory where embeddings and metadata are stored
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_path = self.storage_dir / "embeddings.npz"
        self.metadata_path = self.storage_dir / "metadata.json"
    
    def save_enrollment(self, embeddings: List[np.ndarray], metadata: List[Dict]):
        """
        Save embeddings and metadata to disk
        
        Args:
            embeddings: List of embedding arrays (each shape (512,))
            metadata: List of metadata dicts with pose info
        """
        # Stack embeddings into (N, 512) array
        embeddings_array = np.stack(embeddings, axis=0)
        
        # Save embeddings as compressed numpy file
        np.savez_compressed(
            self.embeddings_path,
            embeddings=embeddings_array,
            version="1.0",
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Save metadata as JSON
        metadata_to_save = {
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(embeddings),
            "frames": metadata
        }
        
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata_to_save, f, indent=2)
    
    def load_embeddings(self) -> Optional[np.ndarray]:
        """
        Load embeddings from disk
        
        Returns:
            numpy array of shape (N, 512) or None if file doesn't exist
        """
        if not self.embeddings_path.exists():
            return None
        
        try:
            data = np.load(self.embeddings_path)
            embeddings = data['embeddings']
            return embeddings
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            return None
    
    def load_metadata(self) -> Optional[Dict]:
        """
        Load metadata from disk
        
        Returns:
            metadata dict or None if file doesn't exist
        """
        if not self.metadata_path.exists():
            return None
        
        try:
            with open(self.metadata_path, 'r') as f:
                metadata = json.load(f)
            return metadata
        except Exception as e:
            print(f"Error loading metadata: {e}")
            return None
    
    def is_enrolled(self) -> bool:
        """
        Check if enrollment data exists
        
        Returns:
            True if both embeddings and metadata files exist
        """
        return self.embeddings_path.exists() and self.metadata_path.exists()
    
    def clear_enrollment(self):
        """Delete both embeddings and metadata files"""
        if self.embeddings_path.exists():
            self.embeddings_path.unlink()
        
        if self.metadata_path.exists():
            self.metadata_path.unlink()
