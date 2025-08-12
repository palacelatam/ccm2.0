/**
 * API Client for CCM Backend
 */

import { auth } from '../../config/firebase';

export interface APIResponse<T> {
  success: boolean;
  message: string;
  data: T;
  errors?: string[];
}

export class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://127.0.0.1:8000') {
    this.baseUrl = baseUrl;
  }

  /**
   * Get Firebase ID token for authentication
   */
  private async getAuthToken(forceRefresh: boolean = false): Promise<string | null> {
    try {
      const user = auth.currentUser;
      if (!user) {
        throw new Error('No authenticated user');
      }
      
      // Force refresh token to get a fresh one with current timestamp
      const token = await user.getIdToken(forceRefresh);
      return token;
    } catch (error) {
      console.error('Failed to get auth token:', error);
      return null;
    }
  }

  /**
   * Make authenticated API request
   */
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {},
    retryCount: number = 0
  ): Promise<APIResponse<T>> {
    const token = await this.getAuthToken(retryCount > 0);
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    // Add authorization header if token is available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle 401 Unauthorized with clock skew retry
    if (response.status === 401 && retryCount === 0) {
      const errorData = await response.json().catch(() => null);
      // Check if it's a clock skew error
      if (errorData?.message?.includes('Token used too early') || 
          errorData?.message?.includes('Invalid token')) {
        console.log('Token timing issue detected, refreshing token and retrying...');
        // Retry once with a fresh token
        return this.request<T>(endpoint, options, 1);
      }
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ 
        message: `HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(errorData.message || `Request failed: ${response.status}`);
    }

    return response.json();
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: any): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * POST request with FormData (for file uploads)
   */
  async postFormData<T>(endpoint: string, formData: FormData): Promise<APIResponse<T>> {
    const token = await this.getAuthToken();
    
    const headers: Record<string, string> = {};

    // Add authorization header if token is available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Don't set Content-Type for FormData - browser will set it with boundary

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ 
        message: `HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(errorData.message || `Request failed: ${response.status}`);
    }

    return response.json();
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data?: any): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PUT request with FormData (for file uploads)
   */
  async putFormData<T>(endpoint: string, formData: FormData): Promise<APIResponse<T>> {
    const token = await this.getAuthToken();
    
    const headers: Record<string, string> = {};

    // Add authorization header if token is available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Don't set Content-Type for FormData - browser will set it with boundary

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ 
        message: `HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(errorData.message || `Request failed: ${response.status}`);
    }

    return response.json();
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  /**
   * Health check endpoint (no auth required)
   */
  async healthCheck(): Promise<APIResponse<any>> {
    const response = await fetch(`${this.baseUrl}/health`);
    return response.json();
  }
}

// Export singleton instance
export const apiClient = new APIClient();