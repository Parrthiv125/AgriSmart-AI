import { apiClient } from './client';

export interface BackendPredictionResponse {
  class_label: string;
  confidence: number;
  disease?: string;
  confidence_pct?: string;
  confidence_level?: string;
  precaution?: string;
  low_confidence_warning?: string | null;
  top_predictions?: Array<{ class: string; confidence: number }>;
}

export const predictionApi = {
  predict: (file: File | Blob, cropHint?: string): Promise<BackendPredictionResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (cropHint) {
      formData.append('crop_hint', cropHint);
    }
    return apiClient.postFormData<BackendPredictionResponse>('/predict', formData);
  }
};
