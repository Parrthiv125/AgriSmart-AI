import { HistoryService } from './HistoryService';
import { HistoryFilter, HistoryItem, HistoryStats } from '../../types/history';
import { MOCK_HISTORY } from '../../data/mockData';

export class MockHistoryService implements HistoryService {
  private historyItems: HistoryItem[] = [];

  constructor() {
    this.historyItems = [...MOCK_HISTORY];
  }

  async getHistory(filter?: HistoryFilter): Promise<HistoryItem[]> {
    await new Promise((res) => setTimeout(res, 250));

    let results = [...this.historyItems];

    if (filter?.searchQuery) {
      const q = filter.searchQuery.toLowerCase();
      results = results.filter(
        (item) =>
          item.crop.toLowerCase().includes(q) ||
          item.diseaseName.toLowerCase().includes(q) ||
          (item.notes && item.notes.toLowerCase().includes(q))
      );
    }

    if (filter?.crop && filter.crop !== 'all') {
      results = results.filter((item) => item.crop.toLowerCase() === filter.crop!.toLowerCase());
    }

    if (filter?.status && filter.status !== 'all') {
      results = results.filter((item) => item.status === filter.status);
    }

    if (filter?.sortBy === 'oldest') {
      results.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());
    } else if (filter?.sortBy === 'confidence') {
      results.sort((a, b) => b.confidence - a.confidence);
    } else {
      // Default: newest first
      results.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    }

    return results;
  }

  async getHistoryItemById(id: string): Promise<HistoryItem | null> {
    await new Promise((res) => setTimeout(res, 150));
    return this.historyItems.find((item) => item.id === id || item.predictionId === id) || null;
  }

  async getHistoryStats(): Promise<HistoryStats> {
    await new Promise((res) => setTimeout(res, 100));
    const totalScans = this.historyItems.length;
    const healthyCount = this.historyItems.filter((i) => i.status === 'healthy').length;
    const diseasedCount = this.historyItems.filter((i) => i.status === 'diseased').length;
    const uncertainCount = this.historyItems.filter((i) => i.status === 'uncertain').length;

    return {
      totalScans,
      healthyCount,
      diseasedCount,
      uncertainCount
    };
  }

  async deleteHistoryItem(id: string): Promise<boolean> {
    await new Promise((res) => setTimeout(res, 200));
    const initialLen = this.historyItems.length;
    this.historyItems = this.historyItems.filter((item) => item.id !== id && item.predictionId !== id);
    return this.historyItems.length < initialLen;
  }

  addHistoryItem(item: HistoryItem): void {
    // Add to start of array
    this.historyItems.unshift(item);
  }
}
