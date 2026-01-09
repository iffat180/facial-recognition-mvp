import { useRef, useState, useCallback, useEffect } from 'react';

export const useCamera = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Pre-create canvas for better performance
  useEffect(() => {
    canvasRef.current = document.createElement('canvas');
  }, []);

  const startCamera = useCallback(async () => {
    // Prevent multiple initializations
    if (streamRef.current) {
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Optimized video constraints for performance
      // Use 'ideal' instead of 'exact' for better browser compatibility
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          frameRate: { ideal: 30, max: 30 },
          facingMode: 'user',
          // Performance hints
          aspectRatio: { ideal: 16/9 }
        },
        audio: false // Explicitly disable audio
      });
      
      streamRef.current = mediaStream;
      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        
        // Wait for video to be ready
        await new Promise<void>((resolve) => {
          if (videoRef.current) {
            const handleLoadedMetadata = () => {
              if (videoRef.current) {
                videoRef.current.play().catch(console.error);
              }
              resolve();
            };
            videoRef.current.onloadedmetadata = handleLoadedMetadata;
            // If already loaded, resolve immediately
            if (videoRef.current.readyState >= 2) {
              handleLoadedMetadata();
            }
          } else {
            resolve();
          }
        });
      }
      
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Camera access denied';
      setError(`Camera error: ${errorMessage}. Please allow camera permissions in your browser.`);
      console.error('Camera access error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop();
      });
      streamRef.current = null;
      setStream(null);
    }
    
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, []);

  const captureFrame = useCallback((): string | null => {
    if (!videoRef.current || !canvasRef.current) {
      console.error('Video or canvas not ready');
      return null;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    // Ensure video is playing
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
      console.error('Video not ready for capture');
      return null;
    }

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d', {
      alpha: false, // Performance: no transparency needed
      willReadFrequently: false // Performance hint
    });
    
    if (!ctx) {
      console.error('Failed to get canvas context');
      return null;
    }

    // CRITICAL: Draw UN-mirrored image for backend
    // The video display is mirrored via CSS, but we capture the original orientation
    // This ensures the backend receives the correct image orientation
    ctx.save();
    
    // Do NOT mirror the canvas context - we want the original orientation
    // The CSS transform on the video element is only for user preview
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    ctx.restore();
    
    // Return base64 JPEG with 85% quality (good balance)
    try {
      return canvas.toDataURL('image/jpeg', 0.85);
    } catch (err) {
      console.error('Failed to convert canvas to data URL:', err);
      return null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  return {
    videoRef,
    startCamera,
    stopCamera,
    captureFrame,
    isActive: !!stream,
    isLoading,
    error
  };
};
