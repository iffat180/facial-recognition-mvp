import React, { useState, useEffect, useCallback } from 'react';
import { useCamera } from '../hooks/useCamera';
import { CameraView } from './CameraView';
import { EnrollmentIntro } from './EnrollmentIntro';
import { enrollUser } from '../api/faceRecognition';
import { Pose, CapturedFrame } from '../types';

const POSE_SEQUENCE: Pose[] = ['front', 'left', 'right', 'up', 'down'];

const POSE_INSTRUCTIONS: Record<Pose, string> = {
  front: "Position your face in the center",
  left: 'Turn your face to the left',
  right: 'Turn your face to the right',
  up: 'Tilt your face upward',
  down: 'Tilt your face downward'
};

const POSE_SUBTEXT: Record<Pose, string> = {
  front: 'Look directly at the camera',
  left: 'Turn your head gently to the left',
  right: 'Turn your head gently to the right',
  up: 'Look up slightly',
  down: 'Look down slightly'
};

export const EnrollmentFlow: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const { videoRef, startCamera, stopCamera, captureFrame, isActive, error: cameraError } = useCamera();
  const [showIntro, setShowIntro] = useState(true);
  const [currentPoseIndex, setCurrentPoseIndex] = useState(0);
  const [capturedFrames, setCapturedFrames] = useState<CapturedFrame[]>([]);
  const [countdown, setCountdown] = useState<number | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentPose = POSE_SEQUENCE[currentPoseIndex];
  const isComplete = currentPoseIndex >= POSE_SEQUENCE.length;

  useEffect(() => {
    if (!showIntro) {
      startCamera();
    }
    return () => stopCamera();
  }, [showIntro, startCamera, stopCamera]);

  useEffect(() => {
    if (countdown === null || countdown === 0) return;
    const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    return () => clearTimeout(timer);
  }, [countdown]);

  useEffect(() => {
    if (countdown === 0) {
      handleCapture();
      setCountdown(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [countdown]);

  const handleStartEnrollment = () => {
    setShowIntro(false);
  };

  const startCountdown = () => {
    if (!isActive) {
      setError('Camera not ready. Please wait.');
      return;
    }
    setError(null);
    setCountdown(3);
  };

  const handleCapture = useCallback(() => {
    const frame = captureFrame();
    if (!frame) {
      setError('Failed to capture frame. Please try again.');
      return;
    }
    
    setCapturedFrames(prev => [...prev, { pose: currentPose, image: frame }]);
    setCurrentPoseIndex(prev => prev + 1);
  }, [captureFrame, currentPose]);

  const handleRetake = () => {
    setCapturedFrames([]);
    setCurrentPoseIndex(0);
    setError(null);
  };

  const handleSubmit = async () => {
    setIsProcessing(true);
    setError(null);
    
    try {
      // Show helpful message for first-time model download
      console.log('Enrolling user... This may take 1-2 minutes on first use while models download.');
      
      const result = await enrollUser(capturedFrames);
      
      if (result.success) {
        // Success! Navigate to verification
        setIsProcessing(false);
        onComplete();
      } else {
        // Enrollment returned success:false
        setError(result.message || 'Enrollment failed. Please try again.');
        setIsProcessing(false);
        // Don't auto-retake, let user decide
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Network error. Make sure the backend is running.';
      setError(errorMessage);
      console.error('Enrollment error:', err);
      setIsProcessing(false);
      // Don't auto-retake on error, let user see the error and decide
    }
  };

  if (showIntro) {
    return <EnrollmentIntro onStart={handleStartEnrollment} />;
  }

  return (
    <div className="enrollment-single-column">
      {/* Compact Header */}
      <div className="enrollment-header-single">
        <h1 className="enrollment-title-single">Face Enrollment</h1>
        <p className="enrollment-subtitle-single">
          {isComplete 
            ? 'Review and complete' 
            : `Step ${currentPoseIndex + 1} of ${POSE_SEQUENCE.length}`}
        </p>
      </div>

      {!isComplete ? (
        <>
          {/* Camera - Single Column */}
          <div className="camera-wrapper-single">
            <CameraView
              videoRef={videoRef}
              showOvalMask={true}
              overlayText={countdown ? countdown.toString() : undefined}
              overlayColor="#4ade80"
              showLandmarkMesh={currentPoseIndex === 0}
            />
          </div>

          {/* Instructions - Below Camera */}
          <div className="instructions-single">
            <h2 className="instruction-title-single">{POSE_INSTRUCTIONS[currentPose]}</h2>
            <p className="instruction-subtitle-single">{POSE_SUBTEXT[currentPose]}</p>
          </div>

          {/* Capture Button */}
          <button
            onClick={startCountdown}
            disabled={countdown !== null || !isActive}
            className={`btn-capture-single ${countdown !== null ? 'btn-capturing' : ''}`}
          >
            {countdown !== null ? `Capturing in ${countdown}...` : 'Capture'}
          </button>

          {/* Progress Dots */}
          <div className="progress-dots-single">
            {POSE_SEQUENCE.map((_, idx) => (
              <div
                key={idx}
                className={`progress-dot ${
                  idx < currentPoseIndex ? 'completed' : 
                  idx === currentPoseIndex ? 'active' : 'pending'
                }`}
              />
            ))}
          </div>

          {/* Error Display */}
          {(error || cameraError) && (
            <div className="error-message-single">
              {error || cameraError}
            </div>
          )}
        </>
      ) : (
        <>
          {/* Completion State */}
          <div className="completion-single">
            <div className="success-icon-single">✓</div>
            <h2 className="instruction-title-single">All captures complete</h2>
            <p className="instruction-subtitle-single">Review your images below</p>
          </div>

          {/* Captured Frames */}
          <div className="captured-grid-single">
            {capturedFrames.map((frame, idx) => (
              <div key={idx} className="frame-item-single">
                <img src={frame.image} alt={frame.pose} />
                <span>{frame.pose}</span>
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="actions-single">
            <button onClick={handleRetake} className="btn-secondary-single" disabled={isProcessing}>
              Retake All
            </button>
            <button 
              onClick={handleSubmit}
              disabled={isProcessing}
              className="btn-success-single"
            >
              {isProcessing ? 'Processing...' : 'Complete Enrollment'}
            </button>
          </div>
          
          {/* Processing status message */}
          {isProcessing && (
            <p className="processing-note">
              Please wait... This may take 1-2 minutes on first use while models download.
            </p>
          )}
          
          {/* Error Display (if enrollment failed but we're still on review screen) */}
          {error && !isProcessing && (
            <div className="error-message-single" style={{ marginTop: '16px' }}>
              {error}
              <button 
                onClick={handleRetake} 
                className="btn-secondary-single" 
                style={{ marginTop: '12px', width: '100%' }}
              >
                Try Again
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};
