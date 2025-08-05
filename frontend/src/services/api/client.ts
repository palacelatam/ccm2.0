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
  private async getAuthToken(): Promise<string | null> {
    try {
      const user = auth.currentUser;
      if (!user) {
        throw new Error('No authenticated user');
      }
      
      const token = await user.getIdToken();
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
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    const token = await this.getAuthToken();
    
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
   * PUT request
   */
  async put<T>(endpoint: string, data?: any): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
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