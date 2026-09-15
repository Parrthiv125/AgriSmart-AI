import { AuthService } from './AuthService';
import { AuthSession, LoginCredentials, RegisterData, User } from '../../types/auth';

export class MockAuthService implements AuthService {
  private currentUser: User | null = null;
  private sessionToken: string | null = null;

  constructor() {
    // Purge any legacy mock user data
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('agrismart_mock_user');

      // Check if real authenticated session exists in storage
      const savedProfile = localStorage.getItem('agrismart_user_profile');
      const savedToken = localStorage.getItem('agrismart_token');
      if (savedProfile && savedToken) {
        try {
          this.currentUser = JSON.parse(savedProfile);
          this.sessionToken = savedToken;
        } catch {
          this.currentUser = null;
          this.sessionToken = null;
        }
      }
    }
  }

  async login(credentials: LoginCredentials): Promise<AuthSession> {
    await new Promise((res) => setTimeout(res, 200));

    if (!credentials.email) {
      throw new Error('Please provide an email or mobile phone number.');
    }

    // Check if an existing profile is in localStorage
    let user: User;
    const savedProfile = typeof window !== 'undefined' ? localStorage.getItem('agrismart_user_profile') : null;
    if (savedProfile) {
      try {
        const parsed = JSON.parse(savedProfile);
        user = {
          ...parsed,
          email: credentials.email
        };
      } catch {
        user = {
          id: `usr_${Date.now()}`,
          name: credentials.email.split('@')[0] || 'User',
          email: credentials.email,
          createdAt: new Date().toISOString()
        };
      }
    } else {
      user = {
        id: `usr_${Date.now()}`,
        name: credentials.email.split('@')[0] || 'User',
        email: credentials.email,
        createdAt: new Date().toISOString()
      };
    }

    const token = `jwt_${Date.now()}`;
    this.currentUser = user;
    this.sessionToken = token;

    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('agrismart_user_profile', JSON.stringify(user));
      localStorage.setItem('agrismart_token', token);
    }

    return {
      user,
      token,
      expiresAt: new Date(Date.now() + 86400000 * 7).toISOString()
    };
  }

  async register(data: RegisterData): Promise<AuthSession> {
    await new Promise((res) => setTimeout(res, 250));

    const user: User = {
      id: `usr_${Date.now()}`,
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
      localStorage.setItem('agrismart_user_profile', JSON.stringify(user));
      localStorage.setItem('agrismart_token', token);
    }

    return {
      user,
      token,
      expiresAt: new Date(Date.now() + 86400000 * 7).toISOString()
    };
  }

  async getCurrentUser(): Promise<User | null> {
    return this.currentUser;
  }

  async logout(): Promise<void> {
    await new Promise((res) => setTimeout(res, 100));
    this.currentUser = null;
    this.sessionToken = null;
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('agrismart_user_profile');
      localStorage.removeItem('agrismart_token');
      localStorage.removeItem('agrismart_mock_user');
    }
  }

  isAuthenticated(): boolean {
    return !!this.currentUser && !!this.sessionToken;
  }
}
