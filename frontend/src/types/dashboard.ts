import { HistoryItem } from './history';
import { PredictionResult } from './prediction';

export interface DashboardMetrics {
  totalScans: number;
  healthyCropsCount: number;
  diseasedCropsCount: number;
  uncertainCount: number;
  scansThisWeek: number;
  healthyPercentage: number;
}

export interface DashboardData {
  metrics: DashboardMetrics;
  latestPrediction?: PredictionResult | null;
  recentScans: HistoryItem[];
  commonCrops: { crop: string; count: number }[];
}
