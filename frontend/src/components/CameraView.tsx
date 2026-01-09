import React from 'react';

interface CameraViewProps {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  showOvalMask?: boolean;
  overlayText?: string;
  overlayColor?: string;
  showLandmarkMesh?: boolean;
}

export const CameraView: React.FC<CameraViewProps> = ({
  videoRef,
  showOvalMask = true,
  overlayText,
  overlayColor = '#4ade80',
  showLandmarkMesh = false
}) => {
  // Facial landmark positions (percentage-based, relative to container)
  // Scaled down to be more compact - face doesn't need to be as close
  const landmarks = [
    // Forehead
    { x: 50, y: 30, id: 'forehead-center' },
    { x: 40, y: 32, id: 'forehead-left' },
    { x: 60, y: 32, id: 'forehead-right' },
    
    // Eyes
    { x: 43, y: 40, id: 'eye-left-outer' },
    { x: 45.5, y: 40, id: 'eye-left-inner' },
    { x: 54.5, y: 40, id: 'eye-right-inner' },
    { x: 57, y: 40, id: 'eye-right-outer' },
    
    // Nose bridge
    { x: 50, y: 44, id: 'nose-bridge' },
    
    // Nose
    { x: 50, y: 50, id: 'nose-tip' },
    { x: 47.5, y: 51.5, id: 'nose-left' },
    { x: 52.5, y: 51.5, id: 'nose-right' },
    
    // Mouth
    { x: 45.5, y: 58, id: 'mouth-left' },
    { x: 50, y: 56.5, id: 'mouth-top' },
    { x: 54.5, y: 58, id: 'mouth-right' },
    { x: 50, y: 61, id: 'mouth-bottom' },
    
    // Jaw
    { x: 38, y: 48, id: 'jaw-left-top' },
    { x: 62, y: 48, id: 'jaw-right-top' },
    { x: 37, y: 60, id: 'jaw-left-bottom' },
    { x: 63, y: 60, id: 'jaw-right-bottom' },
    { x: 50, y: 67, id: 'chin' },
    
    // Cheekbones
    { x: 41, y: 46, id: 'cheek-left' },
    { x: 59, y: 46, id: 'cheek-right' },
  ];

  // Define connections between landmarks (mesh lines)
  const connections = [
    // Forehead outline
    ['forehead-left', 'forehead-center'],
    ['forehead-center', 'forehead-right'],
    
    // Eye structure
    ['eye-left-outer', 'eye-left-inner'],
    ['eye-right-inner', 'eye-right-outer'],
    ['eye-left-inner', 'nose-bridge'],
    ['eye-right-inner', 'nose-bridge'],
    
    // Nose structure
    ['nose-bridge', 'nose-tip'],
    ['nose-tip', 'nose-left'],
    ['nose-tip', 'nose-right'],
    ['nose-left', 'mouth-left'],
    ['nose-right', 'mouth-right'],
    
    // Mouth structure
    ['mouth-left', 'mouth-top'],
    ['mouth-top', 'mouth-right'],
    ['mouth-right', 'mouth-bottom'],
    ['mouth-bottom', 'mouth-left'],
    
    // Jaw structure
    ['forehead-left', 'jaw-left-top'],
    ['forehead-right', 'jaw-right-top'],
    ['jaw-left-top', 'cheek-left'],
    ['jaw-right-top', 'cheek-right'],
    ['cheek-left', 'jaw-left-bottom'],
    ['cheek-right', 'jaw-right-bottom'],
    ['jaw-left-bottom', 'chin'],
    ['jaw-right-bottom', 'chin'],
    
    // Cross connections for mesh density
    ['forehead-center', 'nose-bridge'],
    ['nose-tip', 'mouth-top'],
    ['mouth-top', 'chin'],
    ['eye-left-outer', 'cheek-left'],
    ['eye-right-outer', 'cheek-right'],
    ['cheek-left', 'mouth-left'],
    ['cheek-right', 'mouth-right'],
    ['nose-left', 'cheek-left'],
    ['nose-right', 'cheek-right'],
  ];

  // Get landmark by ID
  const getLandmark = (id: string) => landmarks.find(l => l.id === id);

  return (
    <div className="camera-circle-container">
      {/* Background gradient */}
      <div className="camera-bg-gradient" />
      
      {/* Video with CIRCULAR clip-path */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="camera-video-circle"
        style={{
          transform: 'scaleX(-1)',
          willChange: 'transform',
          backfaceVisibility: 'hidden',
          WebkitBackfaceVisibility: 'hidden',
          // CIRCULAR clip-path - smaller circle
          clipPath: 'circle(35% at 50% 50%)',
          WebkitClipPath: 'circle(35% at 50% 50%)'
        }}
      />
      
      {/* Facial Landmark Mesh Overlay - Only show for first capture */}
      {showOvalMask && showLandmarkMesh && (
        <svg className="facial-mesh-overlay" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice">
          <defs>
            {/* Gradient for mesh */}
            <linearGradient id="meshGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="rgba(255, 255, 255, 0.8)" />
              <stop offset="50%" stopColor="rgba(0, 242, 254, 0.7)" />
              <stop offset="100%" stopColor="rgba(118, 75, 162, 0.7)" />
            </linearGradient>
            
            {/* Glow filter for points */}
            <filter id="pointGlow">
              <feGaussianBlur stdDeviation="0.8" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          {/* Draw connecting lines first (behind dots) */}
          <g className="mesh-lines">
            {connections.map((connection, idx) => {
              const start = getLandmark(connection[0]);
              const end = getLandmark(connection[1]);
              if (!start || !end) return null;
              
              return (
                <line
                  key={`line-${idx}`}
                  x1={start.x}
                  y1={start.y}
                  x2={end.x}
                  y2={end.y}
                  stroke="url(#meshGradient)"
                  strokeWidth="0.1"
                  opacity="0.6"
                  className="mesh-line"
                  style={{
                    animationDelay: `${idx * 0.03}s`
                  }}
                />
              );
            })}
          </g>
          
          {/* Draw landmark points on top */}
          <g className="mesh-points">
            {landmarks.map((point, idx) => (
              <circle
                key={point.id}
                cx={point.x}
                cy={point.y}
                r="0.5"
                fill="white"
                filter="url(#pointGlow)"
                className="mesh-point"
                style={{
                  animationDelay: `${idx * 0.05}s`
                }}
              />
            ))}
          </g>
        </svg>
      )}
      
      {/* Dotted ring overlay - original style */}
      {showOvalMask && (
        <svg className="camera-ring-overlay" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice">
          {/* Main dotted ring - matches video circle */}
          <circle
            cx="50"
            cy="50"
            r="35"
            fill="none"
            stroke="rgba(0, 242, 254, 0.9)"
            strokeWidth="0.3"
            strokeDasharray="2 1.2"
            className="ring-pulse-anim"
          />
          
          {/* Outer glow ring */}
          <circle
            cx="50"
            cy="50"
            r="35.5"
            fill="none"
            stroke="rgba(0, 242, 254, 0.4)"
            strokeWidth="0.2"
          />
        </svg>
      )}
      
      {/* Countdown overlay */}
      {overlayText && (
        <div className="camera-countdown">
          <div className="countdown-bubble">
            <span className="countdown-num">{overlayText}</span>
          </div>
        </div>
      )}
    </div>
  );
};
