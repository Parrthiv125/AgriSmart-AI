import { AuthSession, LoginCredentials, RegisterData, User } from '../../types/auth';

export interface AuthService {
  login(credentials: LoginCredentials): Promise<AuthSession>;
  register(data: RegisterData): Promise<AuthSession>;
  getCurrentUser(): Promise<User | null>;
  logout(): Promise<void>;
  isAuthenticated(): boolean;
}
