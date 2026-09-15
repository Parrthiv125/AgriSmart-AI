import { ApiError } from '../../types/api';

const BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorData: any = {};
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: response.statusText };
      }

      const apiError: ApiError = {
        code: errorData.code || (response.status === 401 ? 'UNAUTHORIZED' : response.status === 404 ? 'NOT_FOUND' : 'SERVER_ERROR'),
        message: errorData.message || `Server request failed with status ${response.status}`,
        farmerFriendlyMessage: errorData.farmerFriendlyMessage || 'Unable to connect with the AgriSmart AI server. Please check your connection.',
        details: errorData.details
      };

      throw apiError;
    }

    return response.json() as Promise<T>;
  }

  private getHeaders(customHeaders: Record<string, string> = {}): Record<string, string> {
    const token = localStorage.getItem('agrismart_token');
    const headers: Record<string, string> = {
      Accept: 'application/json',
      ...customHeaders
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  async get<T>(endpoint: string, queryParams?: Record<string, string | number | boolean | undefined>): Promise<T> {
    let url = `${this.baseUrl}/${endpoint.replace(/^\//, '')}`;
    if (queryParams) {
      const searchParams = new URLSearchParams();
      Object.entries(queryParams).forEach(([key, val]) => {
        if (val !== undefined) searchParams.append(key, String(val));
      });
      const queryString = searchParams.toString();
      if (queryString) url += `?${queryString}`;
    }

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return this.handleResponse<T>(response);
    } catch (err: any) {
      if (err.code) throw err;
      throw this.wrapNetworkError(err);
    }
  }

  async post<T>(endpoint: string, body?: any): Promise<T> {
    const url = `${this.baseUrl}/${endpoint.replace(/^\//, '')}`;
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getHeaders({ 'Content-Type': 'application/json' }),
        body: body ? JSON.stringify(body) : undefined
      });
      return this.handleResponse<T>(response);
    } catch (err: any) {
      if (err.code) throw err;
      throw this.wrapNetworkError(err);
    }
  }

  async postFormData<T>(endpoint: string, formData: FormData): Promise<T> {
    const url = `${this.baseUrl}/${endpoint.replace(/^\//, '')}`;
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getHeaders(), // do not set Content-Type so browser sets boundary
        body: formData
      });
      return this.handleResponse<T>(response);
    } catch (err: any) {
      if (err.code) throw err;
      throw this.wrapNetworkError(err);
    }
  }

  async delete<T>(endpoint: string): Promise<T> {
    const url = `${this.baseUrl}/${endpoint.replace(/^\//, '')}`;
    try {
      const response = await fetch(url, {
        method: 'DELETE',
        headers: this.getHeaders()
      });
      return this.handleResponse<T>(response);
    } catch (err: any) {
      if (err.code) throw err;
      throw this.wrapNetworkError(err);
    }
  }

  private wrapNetworkError(err: Error): ApiError {
    return {
      code: 'NETWORK_ERROR',
      message: err.message || 'Network request failed',
      farmerFriendlyMessage: 'Could not connect to server. Please check your internet connection or try again shortly.'
    };
  }
}

export const apiClient = new ApiClient();
