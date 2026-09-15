import { apiClient } from './client';
import { DashboardData } from '../../types/dashboard';

export const dashboardApi = {
  getDashboardData: (): Promise<DashboardData> => {
    return apiClient.get<DashboardData>('/dashboard');
  }
};
