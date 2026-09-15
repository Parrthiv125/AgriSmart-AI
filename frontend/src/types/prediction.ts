export type ConfidenceLevel = 'high' | 'medium' | 'low';

export interface PredictionDisease {
  classId: string;
  name: string;
  scientificName?: string;
  isHealthy: boolean;
}

export interface PredictionRecommendation {
  title: string;
  summary?: string;
  actions: string[];
}

export interface PredictionResult {
  predictionId: string;
  crop: string;
  disease: PredictionDisease;
  confidence: number;
  confidenceLevel: ConfidenceLevel;
  imageUrl: string;
  explanation: string;
  recommendation: PredictionRecommendation;
  createdAt: string;
  modelName?: string;
}

export interface ScanRequest {
  imageFile: File | Blob;
  cropHint?: string;
  notes?: string;
}
