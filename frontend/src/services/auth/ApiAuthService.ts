import { AuthService } from './AuthService';
import { AuthSession, LoginCredentials, RegisterData, User } from '../../types/auth';
import { authApi } from '../api/authApi';

export class ApiAuthService implements AuthService {
  private currentUser: User | null = null;

  async login(credentials: LoginCredentials): Promise<AuthSession> {
    const session = await authApi.login(credentials);
    this.currentUser = session.user;
    localStorage.setItem('agrismart_token', session.token);
    return session;
  }

  async register(data: RegisterData): Promise<AuthSession> {
    const session = await authApi.register(data);
    this.currentUser = session.user;
    localStorage.setItem('agrismart_token', session.token);
    return session;
  }

  async getCurrentUser(): Promise<User | null> {
    if (this.currentUser) return this.currentUser;
    const token = localStorage.getItem('agrismart_token');
    if (!token) return null;
    try {
      this.currentUser = await authApi.getCurrentUser();
      return this.currentUser;
    } catch {
      localStorage.removeItem('agrismart_token');
      return null;
    }
  }

  async logout(): Promise<void> {
    try {
      await authApi.logout();
    } catch {
      // ignore logout network errors
    } finally {
      this.currentUser = null;
      localStorage.removeItem('agrismart_token');
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('agrismart_token');
  }
}
