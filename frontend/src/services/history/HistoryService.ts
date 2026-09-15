import { HistoryFilter, HistoryItem, HistoryStats } from '../../types/history';

export interface HistoryService {
  getHistory(filter?: HistoryFilter): Promise<HistoryItem[]>;
  getHistoryItemById(id: string): Promise<HistoryItem | null>;
  getHistoryStats(): Promise<HistoryStats>;
  deleteHistoryItem(id: string): Promise<boolean>;
  addHistoryItem(item: HistoryItem): void;
}
