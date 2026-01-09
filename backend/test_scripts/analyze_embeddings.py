import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path
from typing import Tuple, Optional, Dict


def load_enrollment_data() -> Tuple[Optional[np.ndarray], Optional[Dict]]:
    """
    Load enrollment embeddings and metadata from disk
    
    Returns:
        Tuple of (embeddings_array, metadata_dict) or (None, None) if files don't exist
    """
    base_path = Path(__file__).parent.parent
    embeddings_path = base_path / 'face_data' / 'embeddings.npz'
    metadata_path = base_path / 'face_data' / 'metadata.json'
    
    # Load embeddings
    embeddings = None
    if embeddings_path.exists():
        try:
            data = np.load(embeddings_path)
            embeddings = data['embeddings']
            print(f"✓ Loaded embeddings: shape {embeddings.shape}")
        except Exception as e:
            print(f"ERROR: Failed to load embeddings: {e}")
            return None, None
    else:
        print(f"ERROR: Embeddings file not found at {embeddings_path}")
        return None, None
    
    # Load metadata
    metadata = None
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            print(f"✓ Loaded metadata")
        except Exception as e:
            print(f"ERROR: Failed to load metadata: {e}")
            return embeddings, None
    else:
        print(f"WARNING: Metadata file not found at {metadata_path}")
    
    return embeddings, metadata


def compute_cosine_similarity(a: np.ndarray) -> np.ndarray:
    """
    Compute pairwise cosine similarities between embeddings
    
    Args:
        a: Embeddings array of shape (N, 512)
    
    Returns:
        Similarity matrix of shape (N, N)
    """
    # Normalize vectors
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-8)
    
    # Compute pairwise similarities: dot product of normalized vectors
    similarities = np.dot(a_norm, a_norm.T)
    
    return similarities


def analyze_embeddings(embeddings: np.ndarray):
    """
    Analyze embeddings and generate similarity statistics and heatmap
    
    Args:
        embeddings: Embeddings array of shape (N, 512)
    """
    print("\n" + "=" * 50)
    print("EMBEDDING ANALYSIS")
    print("=" * 50)
    
    # Compute pairwise similarities
    print("\nComputing pairwise cosine similarities...")
    similarities = compute_cosine_similarity(embeddings)
    
    # Print similarity matrix
    print("\nSimilarity Matrix:")
    print("-" * 50)
    n = len(embeddings)
    for i in range(n):
        row_str = "  ".join([f"{similarities[i, j]:.2f}" for j in range(n)])
        print(f"  {row_str}")
    print("-" * 50)
    
    # Compute statistics (excluding diagonal which is always 1.0)
    mask = ~np.eye(n, dtype=bool)
    similarities_off_diagonal = similarities[mask]
    
    mean_sim = np.mean(similarities_off_diagonal)
    min_sim = np.min(similarities_off_diagonal)
    max_sim = np.max(similarities_off_diagonal)
    std_sim = np.std(similarities_off_diagonal)
    
    print(f"\nSimilarity Statistics (excluding diagonal):")
    print(f"  Mean:   {mean_sim:.4f}")
    print(f"  Min:    {min_sim:.4f}")
    print(f"  Max:    {max_sim:.4f}")
    print(f"  Std Dev: {std_sim:.4f}")
    
    # Generate heatmap
    print("\nGenerating similarity heatmap...")
    plt.figure(figsize=(10, 8))
    im = plt.imshow(similarities, cmap='viridis', vmin=0, vmax=1, aspect='auto')
    plt.colorbar(im, label='Cosine Similarity')
    plt.title('Embedding Similarity Heatmap', fontsize=14, fontweight='bold')
    plt.xlabel('Embedding Index', fontsize=12)
    plt.ylabel('Embedding Index', fontsize=12)
    
    # Add text annotations
    n = len(embeddings)
    for i in range(n):
        for j in range(n):
            text = plt.text(j, i, f'{similarities[i, j]:.2f}',
                          ha="center", va="center", color="white", fontsize=8)
    
    # Save plot
    base_path = Path(__file__).parent.parent
    output_path = base_path / 'face_data' / 'similarity_heatmap.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Heatmap saved to: {output_path}")
    
    plt.close()
    
    # Print recommendations
    print("\n" + "=" * 50)
    print("RECOMMENDATIONS")
    print("=" * 50)
    
    if min_sim > 0.8:
        print("✓ Very consistent enrollment - recommend threshold 0.7")
        print("  Your face embeddings are highly similar, indicating good enrollment quality.")
    elif min_sim > 0.6:
        print("✓ Good enrollment - recommend threshold 0.6")
        print("  Your face embeddings show reasonable consistency.")
    else:
        print("⚠ Inconsistent enrollment - consider re-enrolling")
        print("  Your face embeddings show low similarity. This may indicate:")
        print("  - Poor lighting conditions during enrollment")
        print("  - Significant pose variations")
        print("  - Face detection issues")
        print("  Consider re-enrolling with better lighting and consistent poses.")
    
    print("=" * 50)


def main():
    """Main execution function"""
    print("=" * 50)
    print("Embedding Analysis Tool")
    print("=" * 50)
    
    # Load data
    embeddings, metadata = load_enrollment_data()
    
    if embeddings is None:
        print("\nERROR: Could not load enrollment data. Please enroll a face first.")
        return
    
    # Print enrollment info
    print("\n" + "=" * 50)
    print("ENROLLMENT INFORMATION")
    print("=" * 50)
    
    if metadata:
        timestamp = metadata.get('timestamp', 'Unknown')
        count = metadata.get('count', len(embeddings))
        print(f"Enrollment timestamp: {timestamp}")
        print(f"Number of embeddings: {count}")
        
        frames = metadata.get('frames', [])
        if frames:
            poses = [f.get('pose', 'unknown') for f in frames]
            print(f"Poses captured: {', '.join(poses)}")
    else:
        print(f"Number of embeddings: {len(embeddings)}")
        print("Metadata not available")
    
    # Analyze embeddings
    analyze_embeddings(embeddings)


if __name__ == '__main__':
    main()
