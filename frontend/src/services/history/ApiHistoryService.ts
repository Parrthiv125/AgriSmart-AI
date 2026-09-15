import { HistoryService } from './HistoryService';
import { HistoryFilter, HistoryItem, HistoryStats } from '../../types/history';
import { historyApi } from '../api/historyApi';

export class ApiHistoryService implements HistoryService {
  async getHistory(filter?: HistoryFilter): Promise<HistoryItem[]> {
    return historyApi.getHistory(filter);
  }

  async getHistoryItemById(id: string): Promise<HistoryItem | null> {
    try {
      return await historyApi.getHistoryItemById(id);
    } catch {
      return null;
    }
  }

  async getHistoryStats(): Promise<HistoryStats> {
    return historyApi.getHistoryStats();
  }

  async deleteHistoryItem(id: string): Promise<boolean> {
    const res = await historyApi.deleteHistoryItem(id);
    return res.success;
  }

  addHistoryItem(_item: HistoryItem): void {
    // Real API persists via prediction endpoint automatically
  }
}
