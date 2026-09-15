import { PredictionService } from './PredictionService';
import { MockPredictionService } from './MockPredictionService';
import { ApiPredictionService } from './ApiPredictionService';

// Default to real backend Model 2 API (set VITE_USE_MOCK_API=true only for standalone frontend mock mode)
const useMock = import.meta.env.VITE_USE_MOCK_API === 'true';

export const predictionService: PredictionService = useMock
  ? new MockPredictionService()
  : new ApiPredictionService();

export * from './PredictionService';
