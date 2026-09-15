import { apiClient } from './client';
import { AuthSession, LoginCredentials, RegisterData, User } from '../../types/auth';

export const authApi = {
  login: (credentials: LoginCredentials): Promise<AuthSession> => {
    return apiClient.post<AuthSession>('/auth/login', credentials);
  },

  register: (data: RegisterData): Promise<AuthSession> => {
    return apiClient.post<AuthSession>('/auth/register', data);
  },

  getCurrentUser: (): Promise<User> => {
    return apiClient.get<User>('/auth/me');
  },

  logout: (): Promise<{ message: string }> => {
    return apiClient.post<{ message: string }>('/auth/logout');
  }
};
