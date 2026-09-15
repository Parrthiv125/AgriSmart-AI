import { AuthService } from './AuthService';
import { AuthSession, LoginCredentials, RegisterData, User } from '../../types/auth';
import { authApi } from '../api/authApi';
import {
  ACTIVE_SESSION_TOKEN_KEY,
  getStableUserId,
  getUserProfileStorageKey,
  getActiveUserId,
  setActiveUserSession,
  clearActiveUserSession
} from './userStorage';

export class ApiAuthService implements AuthService {
  private currentUser: User | null = null;

  async login(credentials: LoginCredentials): Promise<AuthSession> {
    const session = await authApi.login(credentials);
    this.currentUser = session.user;
    const userId = getStableUserId(session.user.email, session.user.id);
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(getUserProfileStorageKey(userId), JSON.stringify(session.user));
      setActiveUserSession(userId, session.token);
    }
    return session;
  }

  async register(data: RegisterData): Promise<AuthSession> {
    const session = await authApi.register(data);
    this.currentUser = session.user;
    const userId = getStableUserId(session.user.email, session.user.id);
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(getUserProfileStorageKey(userId), JSON.stringify(session.user));
      setActiveUserSession(userId, session.token);
    }
    return session;
  }

  async getCurrentUser(): Promise<User | null> {
    if (this.currentUser) return this.currentUser;
    const token = typeof window !== 'undefined' && window.localStorage ? localStorage.getItem(ACTIVE_SESSION_TOKEN_KEY) : null;
    if (!token) return null;

    try {
      this.currentUser = await authApi.getCurrentUser();
      if (this.currentUser) {
        const userId = getStableUserId(this.currentUser.email, this.currentUser.id);
        if (typeof window !== 'undefined' && window.localStorage) {
          localStorage.setItem(getUserProfileStorageKey(userId), JSON.stringify(this.currentUser));
          setActiveUserSession(userId, token);
        }
      }
      return this.currentUser;
    } catch {
      clearActiveUserSession();
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
      clearActiveUserSession();
    }
  }

  isAuthenticated(): boolean {
    const token = typeof window !== 'undefined' && window.localStorage ? localStorage.getItem(ACTIVE_SESSION_TOKEN_KEY) : null;
    const activeUserId = getActiveUserId();
    return !!token && !!activeUserId;
  }
}
