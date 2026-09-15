import { AuthService } from './AuthService';
import { AuthSession, LoginCredentials, RegisterData, User } from '../../types/auth';
import {
  ACTIVE_SESSION_TOKEN_KEY,
  getStableUserId,
  getUserProfileStorageKey,
  getActiveUserId,
  setActiveUserSession,
  clearActiveUserSession
} from './userStorage';

export class MockAuthService implements AuthService {
  private currentUser: User | null = null;
  private sessionToken: string | null = null;

  constructor() {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('agrismart_mock_user');

      // Check if real authenticated active session exists in storage
      const activeUserId = getActiveUserId();
      const savedToken = localStorage.getItem(ACTIVE_SESSION_TOKEN_KEY);

      if (activeUserId && savedToken) {
        const profileKey = getUserProfileStorageKey(activeUserId);
        const savedProfile = localStorage.getItem(profileKey);
        if (savedProfile) {
          try {
            this.currentUser = JSON.parse(savedProfile);
            this.sessionToken = savedToken;
          } catch {
            this.currentUser = null;
            this.sessionToken = null;
          }
        }
      }

      // Legacy fallback migration: if legacy single profile exists, migrate to account-specific key
      if (!this.currentUser) {
        const legacyProfile = localStorage.getItem('agrismart_user_profile');
        if (legacyProfile && savedToken) {
          try {
            const parsed = JSON.parse(legacyProfile);
            if (parsed?.email) {
              const userId = getStableUserId(parsed.email, parsed.id);
              parsed.id = userId;
              this.currentUser = parsed;
              this.sessionToken = savedToken;
              localStorage.setItem(getUserProfileStorageKey(userId), JSON.stringify(parsed));
              setActiveUserSession(userId, savedToken);
              localStorage.removeItem('agrismart_user_profile');
            }
          } catch {
            // ignore
          }
        }
      }
    }
  }

  async login(credentials: LoginCredentials): Promise<AuthSession> {
    await new Promise((res) => setTimeout(res, 200));

    if (!credentials.email) {
      throw new Error('Please provide an email or mobile phone number.');
    }

    const userId = getStableUserId(credentials.email);
    const profileKey = getUserProfileStorageKey(userId);

    let user: User;
    const savedProfile = typeof window !== 'undefined' ? localStorage.getItem(profileKey) : null;
    if (savedProfile) {
      try {
        const parsed = JSON.parse(savedProfile);
        user = {
          ...parsed,
          id: userId,
          email: credentials.email
        };
      } catch {
        user = {
          id: userId,
          name: credentials.email.split('@')[0] || 'User',
          email: credentials.email,
          createdAt: new Date().toISOString()
        };
      }
    } else {
      user = {
        id: userId,
        name: credentials.email.split('@')[0] || 'User',
        email: credentials.email,
        createdAt: new Date().toISOString()
      };
    }

    const token = `jwt_${Date.now()}`;
    this.currentUser = user;
    this.sessionToken = token;

    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(profileKey, JSON.stringify(user));
      setActiveUserSession(userId, token);
    }

    return {
      user,
      token,
      expiresAt: new Date(Date.now() + 86400000 * 7).toISOString()
    };
  }

  async register(data: RegisterData): Promise<AuthSession> {
    await new Promise((res) => setTimeout(res, 250));

    if (!data.email) {
      throw new Error('Please provide an email address.');
    }

    const userId = getStableUserId(data.email);
    const profileKey = getUserProfileStorageKey(userId);

    const user: User = {
      id: userId,
      name: data.name?.trim() || 'User',
      email: data.email,
      farmName: data.farmName?.trim() || undefined,
      location: data.location?.trim() || undefined,
      crops: data.crops && data.crops.length > 0 ? data.crops : [],
      createdAt: new Date().toISOString()
    };

    const token = `jwt_${Date.now()}`;
    this.currentUser = user;
    this.sessionToken = token;

    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(profileKey, JSON.stringify(user));
      setActiveUserSession(userId, token);
    }

    return {
      user,
      token,
      expiresAt: new Date(Date.now() + 86400000 * 7).toISOString()
    };
  }

  async getCurrentUser(): Promise<User | null> {
    if (this.currentUser) return this.currentUser;

    const activeUserId = getActiveUserId();
    if (activeUserId && typeof window !== 'undefined' && window.localStorage) {
      const profileKey = getUserProfileStorageKey(activeUserId);
      const saved = localStorage.getItem(profileKey);
      if (saved) {
        try {
          this.currentUser = JSON.parse(saved);
          return this.currentUser;
        } catch {
          return null;
        }
      }
    }
    return null;
  }

  async logout(): Promise<void> {
    await new Promise((res) => setTimeout(res, 100));
    this.currentUser = null;
    this.sessionToken = null;
    // Clear ONLY active session state, leaving user profiles and histories intact
    clearActiveUserSession();
  }

  isAuthenticated(): boolean {
    return !!this.currentUser && !!this.sessionToken;
  }
}
