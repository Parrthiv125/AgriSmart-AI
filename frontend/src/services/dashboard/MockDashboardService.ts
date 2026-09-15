import { DashboardService } from './DashboardService';
import { DashboardData } from '../../types/dashboard';
import { historyService } from '../history';
import { predictionService } from '../prediction';

export class MockDashboardService implements DashboardService {
  async getDashboardData(): Promise<DashboardData> {
    const history = await historyService.getHistory();
    const stats = await historyService.getHistoryStats();

    const latestHistory = history[0];
    const latestPrediction = latestHistory
      ? await predictionService.getPredictionById(latestHistory.predictionId)
      : null;

    const healthyCount = stats.healthyCount;
    const diseasedCount = stats.diseasedCount;
    const totalScans = stats.totalScans;
    const healthyPercentage = totalScans > 0 ? Math.round((healthyCount / totalScans) * 100) : 100;

    // Aggregate crops
    const cropCountMap: Record<string, number> = {};
    history.forEach((item) => {
      cropCountMap[item.crop] = (cropCountMap[item.crop] || 0) + 1;
    });

    const commonCrops = Object.entries(cropCountMap)
      .map(([crop, count]) => ({ crop, count }))
      .sort((a, b) => b.count - a.count);

    return {
      metrics: {
        totalScans,
        healthyCropsCount: healthyCount,
        diseasedCropsCount: diseasedCount,
        uncertainCount: stats.uncertainCount,
        scansThisWeek: Math.min(totalScans, 7),
        healthyPercentage
      },
      latestPrediction,
      recentScans: history.slice(0, 5),
      commonCrops: commonCrops.length > 0 ? commonCrops : [{ crop: 'Tomato', count: 0 }]
    };
  }
}
