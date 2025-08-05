/**
 * Authentication API Service
 */

import { apiClient, APIResponse } from './client';
import { UserProfile, TokenVerifyResponse, AuthContext } from './types';

export class AuthService {
  /**
   * Verify Firebase token and get user profile
   */
  async verifyToken(token: string): Promise<APIResponse<TokenVerifyResponse>> {
    return apiClient.post<TokenVerifyResponse>('/api/v1/auth/verify', { token });
  }

  /**
   * Get current user's profile
   */
  async getCurrentUserProfile(): Promise<APIResponse<UserProfile>> {
    return apiClient.get<UserProfile>('/api/v1/auth/profile');
  }

  /**
   * Get current user's permissions
   */
  async getCurrentUserPermissions(): Promise<APIResponse<string[]>> {
    return apiClient.get<string[]>('/api/v1/auth/permissions');
  }

  /**
   * Get full authentication context
   */
  async getAuthContext(): Promise<APIResponse<AuthContext>> {
    return apiClient.get<AuthContext>('/api/v1/auth/context');
  }
}

export const authService = new AuthService();