import { apiClient } from './client';
import { HistoryFilter, HistoryItem, HistoryStats } from '../../types/history';

export const historyApi = {
  getHistory: (filter?: HistoryFilter): Promise<HistoryItem[]> => {
    return apiClient.get<HistoryItem[]>('/history', {
      search: filter?.searchQuery,
      crop: filter?.crop,
      status: filter?.status !== 'all' ? filter?.status : undefined,
      sort: filter?.sortBy
    });
  },

  getHistoryItemById: (id: string): Promise<HistoryItem> => {
    return apiClient.get<HistoryItem>(`/history/${id}`);
  },

  getHistoryStats: (): Promise<HistoryStats> => {
    return apiClient.get<HistoryStats>('/history/stats');
  },

  deleteHistoryItem: (id: string): Promise<{ success: boolean }> => {
    return apiClient.delete<{ success: boolean }>(`/history/${id}`);
  }
};
