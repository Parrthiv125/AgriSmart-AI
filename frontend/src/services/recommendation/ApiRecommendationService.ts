import { RecommendationService } from './RecommendationService';
import { RecommendationPlan } from '../../types/recommendation';
import { apiClient } from '../api/client';

export class ApiRecommendationService implements RecommendationService {
  async getRecommendationForDisease(classId: string): Promise<RecommendationPlan | null> {
    try {
      return await apiClient.get<RecommendationPlan>(`/recommendations/${classId}`);
    } catch {
      return null;
    }
  }
}
