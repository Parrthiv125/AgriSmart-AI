import { DashboardService } from './DashboardService';
import { MockDashboardService } from './MockDashboardService';
import { ApiDashboardService } from './ApiDashboardService';

const useMock = import.meta.env.VITE_USE_MOCK_API !== 'false';

export const dashboardService: DashboardService = useMock
  ? new MockDashboardService()
  : new ApiDashboardService();

export * from './DashboardService';
