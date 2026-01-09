import { CapturedFrame, EnrollmentResponse, VerificationResponse, StatusResponse } from '../types';

// Use production URL if available, fallback to localhost for development
// Backend deployed on Railway
const API_BASE = process.env.REACT_APP_API_URL || 'https://facial-recognition-mvp-production.up.railway.app';

export const enrollUser = async (frames: CapturedFrame[]): Promise<EnrollmentResponse> => {
  const response = await fetch(`${API_BASE}/enroll`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ frames })
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Enrollment failed' }));
    throw new Error(errorData.detail || `Enrollment failed: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
};

export const verifyUser = async (image: string): Promise<VerificationResponse> => {
  const response = await fetch(`${API_BASE}/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image })
  });
  if (!response.ok) throw new Error('Verification failed');
  const data = await response.json();
  return {
    verified: data.data?.verified || false,
    confidence: data.data?.similarity || 0,
    message: data.message || ''
  };
};

export const getStatus = async (): Promise<StatusResponse> => {
  const response = await fetch(`${API_BASE}/status`);
  const data = await response.json();
  return {
    enrolled: data.data?.enrolled || false,
    num_embeddings: data.data?.embeddings_count || 0
  };
};

export const clearEnrollment = async (): Promise<void> => {
  await fetch(`${API_BASE}/enrollment`, { method: 'DELETE' });
};
