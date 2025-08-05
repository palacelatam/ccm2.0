/**
 * User Management API Service
 */

import { apiClient, APIResponse } from './client';
import { UserProfile, UserUpdate, Role } from './types';

export class UserService {
  /**
   * Get current user's profile
   */
  async getMyProfile(): Promise<APIResponse<UserProfile>> {
    return apiClient.get<UserProfile>('/api/v1/users/me');
  }

  /**
   * Update current user's profile
   */
  async updateMyProfile(data: UserUpdate): Promise<APIResponse<UserProfile>> {
    return apiClient.put<UserProfile>('/api/v1/users/me', data);
  }

  /**
   * Get user profile by UID
   */
  async getUserProfile(uid: string): Promise<APIResponse<UserProfile>> {
    return apiClient.get<UserProfile>(`/api/v1/users/${uid}`);
  }

  /**
   * Update user profile by UID
   */
  async updateUserProfile(uid: string, data: UserUpdate): Promise<APIResponse<UserProfile>> {
    return apiClient.put<UserProfile>(`/api/v1/users/${uid}`, data);
  }

  /**
   * Get available roles
   */
  async getAvailableRoles(): Promise<APIResponse<Role[]>> {
    return apiClient.get<Role[]>('/api/v1/users/roles/available');
  }
}

export const userService = new UserService();