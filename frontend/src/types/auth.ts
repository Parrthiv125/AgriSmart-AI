export interface User {
  id: string;
  name: string;
  email: string;
  farmName?: string;
  location?: string;
  crops?: string[];
  avatarUrl?: string;
  createdAt: string;
}

export interface LoginCredentials {
  email: string;
  password?: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password?: string;
  farmName?: string;
  location?: string;
  crops?: string[];
}

export interface AuthSession {
  user: User;
  token: string;
  expiresAt: string;
}
