import { DashboardService } from './DashboardService';
import { DashboardData } from '../../types/dashboard';
import { dashboardApi } from '../api/dashboardApi';

export class ApiDashboardService implements DashboardService {
  async getDashboardData(): Promise<DashboardData> {
    return dashboardApi.getDashboardData();
  }
}
