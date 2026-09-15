import { AuthService } from './AuthService';
import { MockAuthService } from './MockAuthService';
import { ApiAuthService } from './ApiAuthService';

const useMock = import.meta.env.VITE_USE_MOCK_API !== 'false';

export const authService: AuthService = useMock
  ? new MockAuthService()
  : new ApiAuthService();

export * from './AuthService';
