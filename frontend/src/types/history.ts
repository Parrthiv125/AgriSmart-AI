import { ConfidenceLevel } from './prediction';

export type HistoryStatus = 'healthy' | 'diseased' | 'uncertain';

export interface HistoryItem {
  id: string;
  predictionId: string;
  crop: string;
  diseaseName: string;
  classId: string;
  confidence: number;
  confidenceLevel: ConfidenceLevel;
  status: HistoryStatus;
  imageUrl: string;
  createdAt: string;
  notes?: string;
}

export interface HistoryFilter {
  searchQuery?: string;
  crop?: string;
  status?: HistoryStatus | 'all';
  sortBy?: 'newest' | 'oldest' | 'confidence';
}

export interface HistoryStats {
  totalScans: number;
  healthyCount: number;
  diseasedCount: number;
  uncertainCount: number;
}
