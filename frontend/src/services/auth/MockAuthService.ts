import { AuthService } from './AuthService';
import { AuthSession, LoginCredentials, RegisterData, User } from '../../types/auth';
import { MOCK_CURRENT_USER } from '../../data/mockData';

export class MockAuthService implements AuthService {
  private currentUser: User | null = null;
  private sessionToken: string | null = null;

  constructor() {
    // Check if session exists in storage
    const savedUser = localStorage.getItem('agrismart_mock_user');
    const savedToken = localStorage.getItem('agrismart_token');
    if (savedUser && savedToken) {
      try {
        this.currentUser = JSON.parse(savedUser);
        this.sessionToken = savedToken;
      } catch {
        this.currentUser = null;
        this.sessionToken = null;
      }
    } else {
      // Default to logged-in demo farmer for zero-friction testing
      this.currentUser = MOCK_CURRENT_USER;
      this.sessionToken = 'mock_jwt_token_demo_farmer_2026';
      localStorage.setItem('agrismart_mock_user', JSON.stringify(MOCK_CURRENT_USER));
      localStorage.setItem('agrismart_token', this.sessionToken);
    }
  }

  async login(credentials: LoginCredentials): Promise<AuthSession> {
    await new Promise((res) => setTimeout(res, 500)); // realistic short latency

    if (!credentials.email) {
      throw new Error('Please provide an email or mobile phone number.');
    }

    const user: User = {
      ...MOCK_CURRENT_USER,
      email: credentials.email,
      name: credentials.email.includes('ramesh') ? 'Ramesh Patel' : credentials.email.split('@')[0] || 'Farmer Partner'
    };

    const token = `mock_jwt_${Date.now()}`;
    this.currentUser = user;
    this.sessionToken = token;
    localStorage.setItem('agrismart_mock_user', JSON.stringify(user));
    localStorage.setItem('agrismart_token', token);

    return {
      user,
      token,
      expiresAt: new Date(Date.now() + 86400000 * 7).toISOString()
    };
  }

  async register(data: RegisterData): Promise<AuthSession> {
    await new Promise((res) => setTimeout(res, 600));

    const user: User = {
      id: `usr_${Date.now()}`,
      name: data.name || 'Farmer Partner',
      email: data.email,
      farmName: data.farmName || 'Family Homestead Farm',
      location: data.location || 'Local Farm District',
      crops: data.crops && data.crops.length > 0 ? data.crops : ['Tomato', 'Potato'],
      createdAt: new Date().toISOString()
    };

    const token = `mock_jwt_${Date.now()}`;
    this.currentUser = user;
    this.sessionToken = token;
    localStorage.setItem('agrismart_mock_user', JSON.stringify(user));
    localStorage.setItem('agrismart_token', token);

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
    await new Promise((res) => setTimeout(res, 200));
    this.currentUser = null;
    this.sessionToken = null;
    localStorage.removeItem('agrismart_mock_user');
    localStorage.removeItem('agrismart_token');
  }

  isAuthenticated(): boolean {
    return !!this.currentUser && !!this.sessionToken;
  }
}
