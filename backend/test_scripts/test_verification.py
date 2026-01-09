import cv2
import base64
import requests
import time
import numpy as np
from typing import Dict, Optional


def check_enrollment_status() -> bool:
    """
    Check if face is enrolled in the system
    
    Returns:
        True if enrolled, False otherwise
    """
    try:
        response = requests.get('http://localhost:8000/status', timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get('data', {}).get('enrolled', False)
    except Exception as e:
        print(f"ERROR: Could not check enrollment status: {e}")
        return False


def verify_continuous(duration_seconds: int = 30):
    """
    Continuous live verification testing
    
    Args:
        duration_seconds: Duration of the test in seconds
    """
    # Check enrollment status
    print("Checking enrollment status...")
    if not check_enrollment_status():
        print("ERROR: No enrollment found. Please enroll a face first using capture_enrollment.py")
        return
    
    print("✓ Enrollment found. Starting verification test...")
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Could not open webcam. Please check your camera connection.")
        return
    
    # Set webcam resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Statistics
    start_time = time.time()
    last_capture_time = 0
    capture_interval = 2  # Capture every 2 seconds
    attempts = 0
    successful_verifications = 0
    confidence_scores = []
    
    print(f"\nStarting verification test ({duration_seconds} seconds)...")
    print("Press 'q' to quit early\n")
    
    while True:
        current_time = time.time()
        elapsed = current_time - start_time
        
        # Check if duration exceeded
        if elapsed >= duration_seconds:
            break
        
        # Read frame
        ret, frame = cap.read()
        if not ret:
            print("ERROR: Failed to capture frame")
            break
        
        height, width = frame.shape[:2]
        
        # Capture and verify every 2 seconds
        if current_time - last_capture_time >= capture_interval:
            # Encode frame to base64
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            b64_str = base64.b64encode(buffer).decode('utf-8')
            
            # Send verification request
            try:
                response = requests.post(
                    'http://localhost:8000/verify',
                    json={'image': f'data:image/jpeg;base64,{b64_str}'},
                    timeout=10
                )
                response.raise_for_status()
                result = response.json()
                
                attempts += 1
                data = result.get('data', {})
                verified = data.get('verified', False)
                similarity = data.get('similarity', 0.0)
                confidence_scores.append(similarity)
                
                if verified:
                    successful_verifications += 1
                    status_color = (0, 255, 0)  # Green
                    status_text = "✓ VERIFIED"
                else:
                    status_color = (0, 0, 255)  # Red
                    status_text = "✗ NOT RECOGNIZED"
                
                # Draw border
                border_thickness = 5
                cv2.rectangle(frame, (0, 0), (width, height), status_color, border_thickness)
                
                # Draw status text
                cv2.putText(frame, status_text, (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, status_color, 3)
                
                # Draw confidence score
                conf_text = f"Confidence: {similarity:.4f}"
                cv2.putText(frame, conf_text, (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                last_capture_time = current_time
                
            except requests.exceptions.ConnectionError:
                cv2.putText(frame, "ERROR: API not available", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            except Exception as e:
                cv2.putText(frame, f"ERROR: {str(e)[:30]}", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Draw FPS and time remaining
        fps = 1.0 / (current_time - start_time + 0.001) if elapsed > 0 else 0
        time_remaining = duration_seconds - elapsed
        
        info_text = f"Time: {int(time_remaining)}s | FPS: {fps:.1f} | Attempts: {attempts}"
        cv2.putText(frame, info_text, (50, height - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show frame
        cv2.imshow('Face Verification Test', frame)
        
        # Check for quit key
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nTest stopped by user")
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    # Print summary
    print("\n" + "=" * 50)
    print("VERIFICATION TEST SUMMARY")
    print("=" * 50)
    print(f"Total attempts: {attempts}")
    if attempts > 0:
        success_rate = (successful_verifications / attempts) * 100
        print(f"Successful verifications: {successful_verifications}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if confidence_scores:
            avg_confidence = np.mean(confidence_scores)
            min_confidence = np.min(confidence_scores)
            max_confidence = np.max(confidence_scores)
            print(f"Average confidence: {avg_confidence:.4f}")
            print(f"Min confidence: {min_confidence:.4f}")
            print(f"Max confidence: {max_confidence:.4f}")
    else:
        print("No verification attempts were made")
    print("=" * 50)


def main():
    """Main execution function"""
    print("=" * 50)
    print("Face Verification Test")
    print("=" * 50)
    verify_continuous(30)


if __name__ == '__main__':
    main()
