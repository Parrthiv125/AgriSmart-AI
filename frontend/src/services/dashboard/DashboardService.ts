import { DashboardData } from '../../types/dashboard';

export interface DashboardService {
  getDashboardData(): Promise<DashboardData>;
}
