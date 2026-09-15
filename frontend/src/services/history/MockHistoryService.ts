import { HistoryService } from './HistoryService';
import { HistoryFilter, HistoryItem, HistoryStats } from '../../types/history';
import { getActiveUserId, getUserHistoryStorageKey } from '../auth/userStorage';

export class MockHistoryService implements HistoryService {
  private historyItems: HistoryItem[] = [];

  constructor() {
    this.loadFromStorage();
  }

  private getActiveHistoryKey(): string | null {
    const activeUserId = getActiveUserId();
    if (activeUserId) {
      return getUserHistoryStorageKey(activeUserId);
    }
    return null;
  }

  private loadFromStorage(): void {
    const storageKey = this.getActiveHistoryKey();
    if (!storageKey) {
      this.historyItems = [];
      return;
    }

    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const saved = localStorage.getItem(storageKey);
        if (saved) {
          this.historyItems = JSON.parse(saved);
          return;
        }
      }
    } catch {
      // ignore JSON parse errors
    }
    this.historyItems = [];
  }

  private saveToStorage(): void {
    const storageKey = this.getActiveHistoryKey();
    if (!storageKey) return;

    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem(storageKey, JSON.stringify(this.historyItems));
      }
    } catch {
      // ignore storage quota errors
    }
  }

  async getHistory(filter?: HistoryFilter): Promise<HistoryItem[]> {
    await new Promise((res) => setTimeout(res, 100));

    // Reload from storage to ensure sync across components and users
    this.loadFromStorage();

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
    await new Promise((res) => setTimeout(res, 50));
    this.loadFromStorage();
    return this.historyItems.find((item) => item.id === id || item.predictionId === id) || null;
  }

  async getHistoryStats(): Promise<HistoryStats> {
    await new Promise((res) => setTimeout(res, 50));
    this.loadFromStorage();
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
    await new Promise((res) => setTimeout(res, 100));
    this.loadFromStorage();
    const initialLen = this.historyItems.length;
    this.historyItems = this.historyItems.filter((item) => item.id !== id && item.predictionId !== id);
    if (this.historyItems.length < initialLen) {
      this.saveToStorage();
      return true;
    }
    return false;
  }

  addHistoryItem(item: HistoryItem): void {
    this.loadFromStorage();
    const storageKey = this.getActiveHistoryKey();
    // Avoid duplicate insertions
    if (!this.historyItems.some((h) => h.id === item.id || h.predictionId === item.predictionId)) {
      this.historyItems.unshift(item);
      if (storageKey) {
        this.saveToStorage();
      }
    }
  }
}
