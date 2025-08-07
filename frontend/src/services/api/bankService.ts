/**
 * Bank administration API service
 */

import { apiClient, APIResponse } from './client';

// Bank Types
export interface Bank {
  id?: string;
  createdAt?: string;
  lastUpdatedAt?: string;
  lastUpdatedBy?: string;
  name: string;
  taxId: string;
  country: string;
  swiftCode?: string;
  status: string;
}

export interface BankCreate {
  name: string;
  taxId: string;
  country: string;
  swiftCode?: string;
  status: string;
}

export interface BankUpdate {
  name?: string;
  taxId?: string;
  country?: string;
  swiftCode?: string;
  status?: string;
}

// Client Segment Types
export interface ClientSegment {
  id?: string;
  createdAt?: string;
  lastUpdatedAt?: string;
  lastUpdatedBy?: string;
  name: string;
  description: string;
  color: string;
}

export interface ClientSegmentCreate {
  name: string;
  description: string;
  color: string;
}

export interface ClientSegmentUpdate {
  name?: string;
  description?: string;
  color?: string;
}

// Settlement Instruction Letter Types
export interface SettlementInstructionLetter {
  id?: string;
  createdAt?: string;
  lastUpdatedAt?: string;
  lastUpdatedBy?: string;
  active: boolean;
  priority: number;
  ruleName: string;
  product: string;
  clientSegmentId?: string;
  documentName: string;
  documentUrl: string;
  templateVariables: string[];
  conditions: Record<string, any>;
}

export interface SettlementInstructionLetterCreate {
  active: boolean;
  priority: number;
  rule_name: string;
  product: string;
  client_segment_id?: string;
  document_name: string;
  document_url: string;
  template_variables: string[];
  conditions: Record<string, any>;
}

export interface SettlementInstructionLetterUpdate {
  active?: boolean;
  priority?: number;
  rule_name?: string;
  product?: string;
  client_segment_id?: string;
  document_name?: string;
  document_url?: string;
  template_variables?: string[];
  conditions?: Record<string, any>;
}

// Bank System Settings Types
export interface BankSystemSettings {
  id?: string;
  createdAt?: string;
  lastUpdatedAt?: string;
  lastUpdatedBy?: string;
  defaultCurrency: string;
  supportedCurrencies: string[];
  supportedProducts: string[];
}

export interface BankSystemSettingsUpdate {
  defaultCurrency?: string;
  supportedCurrencies?: string[];
  supportedProducts?: string[];
}

// Client Assignment Types
export interface ClientSegmentAssignment {
  client_id: string;
  segment_id: string;
}

export interface BulkClientSegmentAssignment {
  assignments: ClientSegmentAssignment[];
}

class BankService {
  // ========== Bank Management Methods ==========
  
  /**
   * Get bank information
   */
  async getBank(bankId: string): Promise<APIResponse<Bank>> {
    return apiClient.get(`/api/v1/banks/${bankId}`);
  }

  /**
   * Update bank information
   */
  async updateBank(bankId: string, updates: BankUpdate): Promise<APIResponse<Bank>> {
    return apiClient.put(`/api/v1/banks/${bankId}`, updates);
  }

  // ========== Client Segmentation Methods ==========

  /**
   * Get all client segments for a bank
   */
  async getClientSegments(bankId: string): Promise<APIResponse<ClientSegment[]>> {
    return apiClient.get(`/api/v1/banks/${bankId}/client-segments`);
  }

  /**
   * Get specific client segment
   */
  async getClientSegment(bankId: string, segmentId: string): Promise<APIResponse<ClientSegment>> {
    return apiClient.get(`/api/v1/banks/${bankId}/client-segments/${segmentId}`);
  }

  /**
   * Create a new client segment
   */
  async createClientSegment(bankId: string, segment: ClientSegmentCreate): Promise<APIResponse<ClientSegment>> {
    return apiClient.post(`/api/v1/banks/${bankId}/client-segments`, segment);
  }

  /**
   * Update client segment
   */
  async updateClientSegment(bankId: string, segmentId: string, updates: ClientSegmentUpdate): Promise<APIResponse<ClientSegment>> {
    return apiClient.put(`/api/v1/banks/${bankId}/client-segments/${segmentId}`, updates);
  }

  /**
   * Delete client segment
   */
  async deleteClientSegment(bankId: string, segmentId: string): Promise<APIResponse<{}>> {
    return apiClient.delete(`/api/v1/banks/${bankId}/client-segments/${segmentId}`);
  }

  // ========== Settlement Instructions Letters Methods ==========

  /**
   * Get all settlement instruction letters for a bank
   */
  async getSettlementLetters(bankId: string): Promise<APIResponse<SettlementInstructionLetter[]>> {
    return apiClient.get(`/api/v1/banks/${bankId}/settlement-letters`);
  }

  /**
   * Get specific settlement instruction letter
   */
  async getSettlementLetter(bankId: string, letterId: string): Promise<APIResponse<SettlementInstructionLetter>> {
    return apiClient.get(`/api/v1/banks/${bankId}/settlement-letters/${letterId}`);
  }

  /**
   * Create a new settlement instruction letter
   */
  async createSettlementLetter(bankId: string, letter: SettlementInstructionLetterCreate): Promise<APIResponse<SettlementInstructionLetter>> {
    return apiClient.post(`/api/v1/banks/${bankId}/settlement-letters`, letter);
  }

  /**
   * Create a new settlement instruction letter with document upload
   */
  async createSettlementLetterWithDocument(
    bankId: string, 
    letterData: {
      rule_name: string;
      product: string;
      client_segment_id?: string;
      priority?: number;
      active?: boolean;
      template_variables?: string[];
      conditions?: Record<string, any>;
    },
    file: File
  ): Promise<APIResponse<SettlementInstructionLetter>> {
    const formData = new FormData();
    
    // Add form fields
    formData.append('rule_name', letterData.rule_name);
    formData.append('product', letterData.product);
    formData.append('priority', String(letterData.priority || 1));
    formData.append('active', String(letterData.active !== false)); // Default to true
    
    if (letterData.client_segment_id) {
      formData.append('client_segment_id', letterData.client_segment_id);
    }
    
    if (letterData.template_variables) {
      formData.append('template_variables', JSON.stringify(letterData.template_variables));
    }
    
    if (letterData.conditions) {
      formData.append('conditions', JSON.stringify(letterData.conditions));
    }
    
    // Add the PDF file
    formData.append('document', file);
    
    return apiClient.postFormData(`/api/v1/banks/${bankId}/settlement-letters/with-document`, formData);
  }

  /**
   * Update settlement instruction letter
   */
  async updateSettlementLetter(bankId: string, letterId: string, updates: SettlementInstructionLetterUpdate): Promise<APIResponse<SettlementInstructionLetter>> {
    return apiClient.put(`/api/v1/banks/${bankId}/settlement-letters/${letterId}`, updates);
  }

  /**
   * Update settlement instruction letter with document replacement
   */
  async updateSettlementLetterWithDocument(
    bankId: string, 
    letterId: string,
    letterData: {
      rule_name: string;
      product: string;
      client_segment_id?: string;
      priority?: number;
      active?: boolean;
      template_variables?: string[];
      conditions?: Record<string, any>;
    },
    file: File
  ): Promise<APIResponse<SettlementInstructionLetter>> {
    const formData = new FormData();
    
    // Add form fields
    formData.append('rule_name', letterData.rule_name);
    formData.append('product', letterData.product);
    formData.append('priority', String(letterData.priority || 1));
    formData.append('active', String(letterData.active !== false)); // Default to true
    
    if (letterData.client_segment_id) {
      formData.append('client_segment_id', letterData.client_segment_id);
    }
    
    if (letterData.template_variables) {
      formData.append('template_variables', JSON.stringify(letterData.template_variables));
    }
    
    if (letterData.conditions) {
      formData.append('conditions', JSON.stringify(letterData.conditions));
    }
    
    // Add the PDF file
    formData.append('document', file);
    
    return apiClient.putFormData(`/api/v1/banks/${bankId}/settlement-letters/${letterId}/with-document`, formData);
  }

  /**
   * Delete settlement instruction letter
   */
  async deleteSettlementLetter(bankId: string, letterId: string): Promise<APIResponse<{}>> {
    return apiClient.delete(`/api/v1/banks/${bankId}/settlement-letters/${letterId}`);
  }

  /**
   * Preview settlement instruction letter document - generates signed URL
   */
  async previewSettlementLetterDocument(bankId: string, letterId: string, expirationMinutes?: number): Promise<APIResponse<{signed_url: string, expires_in_minutes: number, document_name: string}>> {
    const params = expirationMinutes ? `?expiration_minutes=${expirationMinutes}` : '';
    return apiClient.get(`/api/v1/banks/${bankId}/settlement-letters/${letterId}/document/preview${params}`);
  }

  /**
   * Delete settlement instruction letter document
   */
  async deleteSettlementLetterDocument(bankId: string, letterId: string): Promise<APIResponse<{document_path: string, deleted_from_storage: boolean, database_updated: boolean}>> {
    return apiClient.delete(`/api/v1/banks/${bankId}/settlement-letters/${letterId}/document`);
  }

  // ========== Client Assignment Methods ==========

  /**
   * Get all client-segment assignments for a bank
   */
  async getClientSegmentAssignments(bankId: string): Promise<APIResponse<Record<string, string[]>>> {
    return apiClient.get(`/api/v1/banks/${bankId}/client-assignments`);
  }

  /**
   * Assign a client to a segment
   */
  async assignClientToSegment(bankId: string, assignment: ClientSegmentAssignment): Promise<APIResponse<{}>> {
    return apiClient.post(`/api/v1/banks/${bankId}/client-assignments/assign`, assignment);
  }

  /**
   * Bulk assign clients to segments
   */
  async bulkAssignClientsToSegments(bankId: string, assignments: BulkClientSegmentAssignment): Promise<APIResponse<{}>> {
    return apiClient.post(`/api/v1/banks/${bankId}/client-assignments/bulk-assign`, assignments);
  }

  /**
   * Remove a client from a segment
   */
  async removeClientFromSegment(bankId: string, clientId: string, segmentId: string): Promise<APIResponse<{}>> {
    return apiClient.delete(`/api/v1/banks/${bankId}/client-assignments/${clientId}/${segmentId}`);
  }

  // ========== Bank System Settings Methods ==========

  /**
   * Get bank system settings
   */
  async getBankSystemSettings(bankId: string): Promise<APIResponse<BankSystemSettings>> {
    return apiClient.get(`/api/v1/banks/${bankId}/system-settings`);
  }

  /**
   * Update bank system settings
   */
  async updateBankSystemSettings(bankId: string, settings: BankSystemSettingsUpdate): Promise<APIResponse<BankSystemSettings>> {
    return apiClient.put(`/api/v1/banks/${bankId}/system-settings`, settings);
  }

  // ========== Document Upload Helper Methods ==========

  /**
   * Upload a settlement instruction letter document
   * Note: This is a placeholder for file upload functionality
   * In a real implementation, you'd handle file uploads to cloud storage
   */
  async uploadSettlementDocument(bankId: string, file: File): Promise<APIResponse<{ documentUrl: string; documentName: string }>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('bankId', bankId);

    // This would typically upload to cloud storage and return the URL
    // For now, return a mock response
    return {
      success: true,
      message: 'Document uploaded successfully',
      data: {
        documentUrl: `https://storage.googleapis.com/ccm-documents/${bankId}/${file.name}`,
        documentName: file.name
      }
    };
  }

  /**
   * Delete a settlement instruction letter document
   */
  async deleteSettlementDocument(bankId: string, documentUrl: string): Promise<APIResponse<{}>> {
    // This would typically delete from cloud storage
    // For now, return a mock response
    return {
      success: true,
      message: 'Document deleted successfully',
      data: {}
    };
  }

  // ========== Client Management Methods ==========

  /**
   * Get all clients (independent of banks)
   */
  async getAllClients(): Promise<APIResponse<any[]>> {
    return apiClient.get(`/api/v1/clients`);
  }
}

export const bankService = new BankService();