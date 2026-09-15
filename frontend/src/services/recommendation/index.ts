import { RecommendationService } from './RecommendationService';
import { MockRecommendationService } from './MockRecommendationService';
import { ApiRecommendationService } from './ApiRecommendationService';

const useMock = import.meta.env.VITE_USE_MOCK_API !== 'false';

export const recommendationService: RecommendationService = useMock
  ? new MockRecommendationService()
  : new ApiRecommendationService();

export * from './RecommendationService';
