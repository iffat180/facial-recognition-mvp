import React from 'react';

interface EnrollmentIntroProps {
  onStart: () => void;
  onSkipToVerification?: () => void;
}

export const EnrollmentIntro: React.FC<EnrollmentIntroProps> = ({ 
  onStart, 
  onSkipToVerification 
}) => {
  return (
    <div className="enrollment-intro-container">
      {/* Background with gradient */}
      <div className="intro-background" />
      
      {/* Content Card */}
      <div className="intro-card">
        {/* Biometric Icon */}
        <div className="face-icon-container">
          <svg className="face-icon" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="iconGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#764ba2" />
                <stop offset="100%" stopColor="#0f4c75" />
              </linearGradient>
            </defs>
            
            {/* Face outline with grid */}
            <ellipse 
              cx="50" 
              cy="50" 
              rx="30" 
              ry="38" 
              fill="none" 
              stroke="url(#iconGradient)" 
              strokeWidth="2"
              strokeDasharray="4 2"
            />
            
            {/* Crosshair grid */}
            <line x1="50" y1="15" x2="50" y2="85" stroke="url(#iconGradient)" strokeWidth="1" opacity="0.5" />
            <line x1="23" y1="50" x2="77" y2="50" stroke="url(#iconGradient)" strokeWidth="1" opacity="0.5" />
          </svg>
        </div>
        
        {/* Title */}
        <h1 className="intro-title">Face<span className="title-accent">ID</span></h1>
        
        {/* Description */}
        <p className="intro-description">
          Secure biometric authentication using facial recognition. 
          We'll capture your face from multiple angles to create a unique profile.
        </p>
        
        {/* Get Started Button */}
        <button onClick={onStart} className="btn btn-primary btn-large intro-cta">
          Get Started
        </button>
        
        {/* Optional: Skip to verification link */}
        {onSkipToVerification && (
          <button 
            onClick={onSkipToVerification} 
            className="intro-skip-link"
          >
            Already enrolled? Test verification
          </button>
        )}
      </div>
    </div>
  );
};
