export interface RecommendationAction {
  id: string;
  category: 'immediate' | 'organic' | 'chemical' | 'cultural';
  title: string;
  description: string;
  isUrgent?: boolean;
}

export interface RecommendationPlan {
  classId: string;
  diseaseName: string;
  crop: string;
  urgencyLevel: 'low' | 'moderate' | 'high' | 'critical';
  headline: string;
  summary: string;
  actions: RecommendationAction[];
  disclaimer: string;
}
