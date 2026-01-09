import React, { useState, useEffect } from 'react';
import { getStatus, clearEnrollment } from '../api/faceRecognition';
import { StatusResponse } from '../types';

interface StatusCheckProps {
  onEnroll: () => void;
  onVerify: () => void;
}

export const StatusCheck: React.FC<StatusCheckProps> = ({ onEnroll, onVerify }) => {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    setLoading(true);
    try {
      const result = await getStatus();
      setStatus(result);
    } catch (error) {
      console.error('Failed to check status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClearEnrollment = async () => {
    if (!window.confirm('Are you sure you want to clear enrollment?')) return;
    
    try {
      await clearEnrollment();
      await checkStatus();
    } catch (error) {
      alert('Failed to clear enrollment');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="card" style={{ marginTop: '40px' }}>
      <div className="card-header">
        <h1 className="card-title">Face Recognition MVP</h1>
        <p className="card-subtitle">Secure biometric authentication</p>
      </div>
      
      <div className={`status-badge ${status?.enrolled ? 'enrolled' : 'not-enrolled'}`}>
        {status?.enrolled 
          ? `✓ Enrolled (${status.num_embeddings} embeddings)` 
          : '○ Not enrolled'}
      </div>
      
      <div className="action-buttons">
        {!status?.enrolled ? (
          <button onClick={onEnroll} className="btn btn-primary">
            Start Enrollment
          </button>
        ) : (
          <>
            <button onClick={onVerify} className="btn btn-success">
              Test Verification
            </button>
            <button onClick={handleClearEnrollment} className="btn btn-danger">
              Clear Enrollment
            </button>
          </>
        )}
      </div>
    </div>
  );
};
