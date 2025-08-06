/**
 * API Services Barrel Export
 */

export * from './client';
export * from './types';
export * from './authService';
export * from './userService';
export * from './clientService';
export * from './bankService';

// Re-export service instances for easy access
export { apiClient } from './client';
export { authService } from './authService';
export { userService } from './userService';
export { clientService } from './clientService';
export { bankService } from './bankService';