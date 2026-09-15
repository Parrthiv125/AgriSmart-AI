import { HistoryService } from './HistoryService';
import { MockHistoryService } from './MockHistoryService';

// Client-side persistent history service via localStorage
export const historyService: HistoryService = new MockHistoryService();

export * from './HistoryService';
