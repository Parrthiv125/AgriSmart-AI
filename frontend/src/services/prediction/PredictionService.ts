import { PredictionResult } from '../../types/prediction';

export interface PredictionService {
  predict(imageFile: File | Blob, cropHint?: string): Promise<PredictionResult>;
  getPredictionById(predictionId: string): Promise<PredictionResult | null>;
}
