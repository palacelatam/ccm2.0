/**
 * API Types matching backend models
 */

export interface UserProfile {
  uid: string;
  email: string;
  firstName: string;
  lastName: string;
  fullName: string;
  primaryRole?: string;
  organization?: OrganizationReference;
  language: string;
  timezone: string;
  status: string;
  emailVerified: boolean;
  twoFactorEnabled: boolean;
  lastLoginAt?: string;
}

export interface OrganizationReference {
  id: string;
  name: string;
  type: string; // 'bank' or 'client'
}

export interface UserUpdate {
  firstName?: string;
  lastName?: string;
  language?: string;
  timezone?: string;
  status?: string;
}

export interface Role {
  displayName: string;
  description: string;
  permissions: string[];
  createdAt?: string;
  lastUpdatedAt?: string;
}

export interface AuthContext {
  uid: string;
  email: string;
  userProfile?: UserProfile;
  permissions: string[];
  organizationId?: string;
  organizationType?: string;
}

export interface TokenVerifyResponse {
  success: boolean;
  userProfile: UserProfile;
  permissions: string[];
}