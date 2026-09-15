import { RecommendationPlan } from '../../types/recommendation';

export interface RecommendationService {
  getRecommendationForDisease(classId: string): Promise<RecommendationPlan | null>;
}
