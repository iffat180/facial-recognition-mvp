import React, { useState, useEffect, useRef } from 'react';
import { useCamera } from '../hooks/useCamera';
import { CameraView } from './CameraView';
import { verifyUser } from '../api/faceRecognition';

export const VerificationFlow: React.FC = () => {
  const { videoRef, startCamera, stopCamera, captureFrame } = useCamera();
  const [isVerifying, setIsVerifying] = useState(false);
  const [result, setResult] = useState<{ verified: boolean; confidence: number } | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const isVerifyingRef = useRef(false);

  useEffect(() => {
    isVerifyingRef.current = isVerifying;
  }, [isVerifying]);

  useEffect(() => {
    startCamera();
    
    const startVerification = () => {
      intervalRef.current = setInterval(async () => {
        if (isVerifyingRef.current) return;
        
        const frame = captureFrame();
        if (!frame) return;

        setIsVerifying(true);
        try {
          const verifyResult = await verifyUser(frame);
          setResult(verifyResult);
        } catch (error) {
          console.error('Verification error:', error);
        } finally {
          setIsVerifying(false);
        }
      }, 2000);
    };
    
    startVerification();
    
    return () => {
      stopCamera();
      if (intervalRef.current !== undefined) clearInterval(intervalRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount

  return (
    <div className="card verification-card">
      <div className="card-header">
        <h1 className="card-title">Face Verification</h1>
        <p className="card-subtitle">Real-time biometric authentication</p>
      </div>

      <div className="camera-wrapper-single verification-camera-wrapper">
        <CameraView videoRef={videoRef} showOvalMask={true} />
        
        <div className={`verification-status ${
          isVerifying ? 'verifying' : 
          result?.verified ? 'verified' : 'not-verified'
        }`}>
          {isVerifying ? (
            'Verifying...'
          ) : result ? (
            <>
              <div className="status-icon">
                {result.verified ? '✓' : '✗'}
              </div>
              <div className="status-text">
                {result.verified ? 'VERIFIED' : 'NOT RECOGNIZED'}
              </div>
              <div className="confidence">
                Confidence: {(result.confidence * 100).toFixed(1)}%
              </div>
            </>
          ) : (
            'Position your face in frame'
          )}
        </div>
      </div>
      
      <div className="test-enrollment-link">
        <p>Enrolled user detected. Testing real-time verification.</p>
      </div>
    </div>
  );
};
