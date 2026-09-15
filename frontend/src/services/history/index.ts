import { HistoryService } from './HistoryService';
import { MockHistoryService } from './MockHistoryService';
import { ApiHistoryService } from './ApiHistoryService';

const useMock = import.meta.env.VITE_USE_MOCK_API !== 'false';

export const historyService: HistoryService = useMock
  ? new MockHistoryService()
  : new ApiHistoryService();

export * from './HistoryService';
