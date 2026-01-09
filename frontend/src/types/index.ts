export type Pose = 'front' | 'left' | 'right' | 'up' | 'down';

export interface CapturedFrame {
  pose: Pose;
  image: string;
}

export interface EnrollmentResponse {
  success: boolean;
  message: string;
  metadata?: Array<{
    pose: string;
    confidence: number;
    face_ratio: number;
  }>;
  errors?: string[];
}

export interface VerificationResponse {
  verified: boolean;
  confidence: number;
  message: string;
}

export interface StatusResponse {
  enrolled: boolean;
  num_embeddings: number;
}
