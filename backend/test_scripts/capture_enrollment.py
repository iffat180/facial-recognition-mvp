import cv2
import base64
import requests
import time
from typing import List, Dict
from pathlib import Path


def capture_poses() -> List[Dict]:
    """
    Interactive webcam capture for face enrollment poses
    
    Returns:
        List of dictionaries with 'pose' and 'image' (base64) keys
    """
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Could not open webcam. Please check your camera connection.")
        return []
    
    # Set webcam resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Define poses
    POSES = ['front', 'left', 'right', 'up', 'down']
    captured_frames = []
    
    print("\n=== Face Enrollment Capture ===")
    print("Instructions:")
    print("- Position your face in the center of the frame")
    print("- Press SPACE when ready for each pose")
    print("- A 3-2-1 countdown will appear before capture")
    print("- Press 'q' at any time to quit\n")
    
    for pose in POSES:
        print(f"\nPreparing to capture: {pose.upper()}")
        print("Position your face and press SPACE when ready...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Failed to capture frame from camera")
                cap.release()
                cv2.destroyAllWindows()
                return []
            
            # Display instructions
            height, width = frame.shape[:2]
            text = f"Position: {pose.upper()} - Press SPACE when ready"
            cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, "Press 'q' to quit", (50, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
            
            cv2.imshow('Face Enrollment', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # SPACE key
                break
            elif key == ord('q'):  # Quit
                print("\nCapture cancelled by user")
                cap.release()
                cv2.destroyAllWindows()
                return []
        
        # Countdown
        print(f"Capturing {pose} in...")
        for countdown in [3, 2, 1]:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Failed to capture frame during countdown")
                cap.release()
                cv2.destroyAllWindows()
                return []
            
            height, width = frame.shape[:2]
            countdown_text = str(countdown)
            text_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 3, 5)[0]
            text_x = (width - text_size[0]) // 2
            text_y = (height + text_size[1]) // 2
            
            cv2.putText(frame, countdown_text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5)
            cv2.putText(frame, f"Position: {pose.upper()}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.imshow('Face Enrollment', frame)
            cv2.waitKey(1)
            time.sleep(1)
        
        # Capture frame
        ret, frame = cap.read()
        if not ret:
            print(f"ERROR: Failed to capture frame for {pose}")
            continue
        
        # Show "Captured!" message
        height, width = frame.shape[:2]
        cv2.putText(frame, "Captured!", (width // 2 - 150, height // 2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        cv2.imshow('Face Enrollment', frame)
        cv2.waitKey(1)
        time.sleep(1)
        
        # Encode frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        b64_str = base64.b64encode(buffer).decode('utf-8')
        
        # Store frame
        frame_data = {
            'pose': pose,
            'image': f'data:image/jpeg;base64,{b64_str}'
        }
        captured_frames.append(frame_data)
        
        # Save frame to test_images directory for debugging
        test_images_dir = Path(__file__).parent.parent / 'test_images'
        test_images_dir.mkdir(exist_ok=True)
        image_path = test_images_dir / f'{pose}.jpg'
        cv2.imwrite(str(image_path), frame)
        print(f"✓ Captured {pose} (saved to {image_path})")
    
    # Release camera and close windows
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n✓ Successfully captured {len(captured_frames)} poses")
    return captured_frames


def enroll_user(frames: List[Dict]) -> Dict:
    """
    Send captured frames to enrollment endpoint
    
    Args:
        frames: List of frame dictionaries with pose and image data
    
    Returns:
        Response JSON from API
    """
    url = 'http://localhost:8000/enroll'
    
    try:
        print(f"\nSending {len(frames)} frames to enrollment endpoint...")
        response = requests.post(url, json={'frames': frames}, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API. Is the server running at http://localhost:8000?")
        return {'success': False, 'error': 'Connection error'}
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out. The enrollment process may be taking too long.")
        return {'success': False, 'error': 'Timeout error'}
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: HTTP error occurred: {e}")
        try:
            error_data = response.json()
            return error_data
        except:
            return {'success': False, 'error': str(e)}
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return {'success': False, 'error': str(e)}


def main():
    """Main execution function"""
    print("=" * 50)
    print("Face Enrollment - Follow pose instructions")
    print("=" * 50)
    
    # Capture poses
    frames = capture_poses()
    
    if not frames:
        print("\nNo frames captured. Exiting.")
        return
    
    if len(frames) < 5:
        print(f"\nWARNING: Only {len(frames)} frames captured. Minimum 5 required.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Enrollment cancelled.")
            return
    
    # Enroll user
    result = enroll_user(frames)
    
    # Print results
    print("\n" + "=" * 50)
    print("ENROLLMENT RESULT")
    print("=" * 50)
    
    if result.get('success', False):
        print("✓ Enrollment successful!")
        data = result.get('data', {})
        embeddings_count = data.get('embeddings_count', 0)
        print(f"  - Embeddings saved: {embeddings_count}")
        
        metadata = data.get('metadata', [])
        if metadata:
            poses = [m.get('pose', 'unknown') for m in metadata]
            print(f"  - Valid poses: {', '.join(poses)}")
        
        errors = data.get('errors')
        if errors:
            print(f"  - Warnings: {len(errors)} frames had errors")
    else:
        print("✗ Enrollment failed!")
        error_msg = result.get('error') or result.get('detail', 'Unknown error')
        print(f"  - Error: {error_msg}")
    
    print("=" * 50)


if __name__ == '__main__':
    main()
