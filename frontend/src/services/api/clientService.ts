/**
 * Client settings API service
 */

import { apiClient, APIResponse } from './client';

// Client Settings Types
export interface AutoConfirmSettings {
  enabled: boolean;
  delayMinutes: number;
}

export interface AutomationSettings {
  dataSharing: boolean;
  autoConfirmMatched: AutoConfirmSettings;
  autoCartaInstruccion: boolean;
  autoConfirmDisputed: AutoConfirmSettings;
}

export interface EmailAlertSettings {
  enabled: boolean;
  emails: string[];
}

export interface WhatsappAlertSettings {
  enabled: boolean;
  phones: string[];
}

export interface AlertSettings {
  emailConfirmedTrades: EmailAlertSettings;
  emailDisputedTrades: EmailAlertSettings;
  whatsappConfirmedTrades: WhatsappAlertSettings;
  whatsappDisputedTrades: WhatsappAlertSettings;
}

export interface PreferencesSettings {
  language: string;
  timezone: string;
  dateFormat: string;
  numberFormat: string;
}

export interface ClientSettings {
  id?: string;
  createdAt?: string;
  lastUpdatedAt?: string;
  lastUpdatedBy?: string;
  automation: AutomationSettings;
  alerts: AlertSettings;
  preferences: PreferencesSettings;
}

export interface ClientSettingsUpdate {
  automation?: Partial<AutomationSettings>;
  alerts?: Partial<AlertSettings>;
  preferences?: Partial<PreferencesSettings>;
}

// Bank Account Types
export interface BankAccount {
  id?: string;
  createdAt?: string;
  lastUpdatedAt?: string;
  lastUpdatedBy?: string;
  active: boolean;
  accountName: string;
  bankName: string;
  swiftCode: string;
  accountCurrency: string;
  accountNumber: string;
  isDefault: boolean;
}

export interface BankAccountCreate {
  accountName: string;
  bankName: string;
  swiftCode: string;
  accountCurrency: string;
  accountNumber: string;
  isDefault: boolean;
}

export interface BankAccountUpdate {
  active?: boolean;
  accountName?: string;
  bankName?: string;
  swiftCode?: string;
  accountCurrency?: string;
  accountNumber?: string;
  isDefault?: boolean;
}

// Settlement Rule Types
export interface SettlementRule {
  id?: string;
  createdAt?: string;
  lastUpdatedAt?: string;
  lastUpdatedBy?: string;
  active: boolean;
  priority: number;
  name: string;
  counterparty: string;
  cashflowCurrency: string;
  direction: string;
  product: string;
  bankAccountId: string;
}

export interface SettlementRuleCreate {
  name: string;
  counterparty: string;
  cashflowCurrency: string;
  direction: string;
  product: string;
  bankAccountId: string;
  priority: number;
}

export interface SettlementRuleUpdate {
  active?: boolean;
  priority?: number;
  name?: string;
  counterparty?: string;
  cashflowCurrency?: string;
  direction?: string;
  product?: string;
  bankAccountId?: string;
}

// Data Mapping Types
export interface FieldTransformation {
  type: string;
  params: Record<string, any>;
}

export interface FieldMapping {
  sourceField: string;
  targetField: string;
  transformation: FieldTransformation;
}

export interface ExpectedField {
  name: string;
  type: string;
  required: boolean;
  format?: string;
  enumValues?: string[];
}

export interface DataMapping {
  id?: string;
  createdAt?: string;
  lastUpdatedAt?: string;
  lastUpdatedBy?: string;
  name: string;
  description: string;
  fileType: string;
  isDefault: boolean;
  fieldMappings: FieldMapping[];
  expectedFields: ExpectedField[];
  lastUsedAt?: string;
  usageCount: number;
}

export interface DataMappingCreate {
  name: string;
  description: string;
  fileType: string;
  isDefault: boolean;
  fieldMappings: FieldMapping[];
  expectedFields: ExpectedField[];
}

export interface DataMappingUpdate {
  name?: string;
  description?: string;
  fileType?: string;
  isDefault?: boolean;
  fieldMappings?: FieldMapping[];
  expectedFields?: ExpectedField[];
}

class ClientService {
  // ========== Client Settings Methods ==========
  
  /**
   * Get client settings configuration
   */
  async getClientSettings(clientId: string): Promise<APIResponse<ClientSettings>> {
    return apiClient.get(`/api/v1/clients/${clientId}/settings`);
  }

  /**
   * Update client settings configuration
   */
  async updateClientSettings(clientId: string, settings: ClientSettingsUpdate): Promise<APIResponse<ClientSettings>> {
    return apiClient.put(`/api/v1/clients/${clientId}/settings`, settings);
  }

  // ========== Bank Account Methods ==========

  /**
   * Get all bank accounts for a client
   */
  async getBankAccounts(clientId: string): Promise<APIResponse<BankAccount[]>> {
    return apiClient.get(`/api/v1/clients/${clientId}/bank-accounts`);
  }

  /**
   * Get specific bank account
   */
  async getBankAccount(clientId: string, accountId: string): Promise<APIResponse<BankAccount>> {
    return apiClient.get(`/api/v1/clients/${clientId}/bank-accounts/${accountId}`);
  }

  /**
   * Create a new bank account
   */
  async createBankAccount(clientId: string, account: BankAccountCreate): Promise<APIResponse<BankAccount>> {
    return apiClient.post(`/api/v1/clients/${clientId}/bank-accounts`, account);
  }

  /**
   * Update bank account
   */
  async updateBankAccount(clientId: string, accountId: string, updates: BankAccountUpdate): Promise<APIResponse<BankAccount>> {
    return apiClient.put(`/api/v1/clients/${clientId}/bank-accounts/${accountId}`, updates);
  }

  /**
   * Delete bank account
   */
  async deleteBankAccount(clientId: string, accountId: string): Promise<APIResponse<{}>> {
    return apiClient.delete(`/api/v1/clients/${clientId}/bank-accounts/${accountId}`);
  }

  // ========== Settlement Rules Methods ==========

  /**
   * Get all settlement rules for a client
   */
  async getSettlementRules(clientId: string): Promise<APIResponse<SettlementRule[]>> {
    return apiClient.get(`/api/v1/clients/${clientId}/settlement-rules`);
  }

  /**
   * Get specific settlement rule
   */
  async getSettlementRule(clientId: string, ruleId: string): Promise<APIResponse<SettlementRule>> {
    return apiClient.get(`/api/v1/clients/${clientId}/settlement-rules/${ruleId}`);
  }

  /**
   * Create a new settlement rule
   */
  async createSettlementRule(clientId: string, rule: SettlementRuleCreate): Promise<APIResponse<SettlementRule>> {
    return apiClient.post(`/api/v1/clients/${clientId}/settlement-rules`, rule);
  }

  /**
   * Update settlement rule
   */
  async updateSettlementRule(clientId: string, ruleId: string, updates: SettlementRuleUpdate): Promise<APIResponse<SettlementRule>> {
    return apiClient.put(`/api/v1/clients/${clientId}/settlement-rules/${ruleId}`, updates);
  }

  /**
   * Delete settlement rule
   */
  async deleteSettlementRule(clientId: string, ruleId: string): Promise<APIResponse<{}>> {
    return apiClient.delete(`/api/v1/clients/${clientId}/settlement-rules/${ruleId}`);
  }

  // ========== Data Mapping Methods ==========

  /**
   * Get all data mappings for a client
   */
  async getDataMappings(clientId: string): Promise<APIResponse<DataMapping[]>> {
    return apiClient.get(`/api/v1/clients/${clientId}/data-mappings`);
  }

  /**
   * Get specific data mapping
   */
  async getDataMapping(clientId: string, mappingId: string): Promise<APIResponse<DataMapping>> {
    return apiClient.get(`/api/v1/clients/${clientId}/data-mappings/${mappingId}`);
  }

  /**
   * Create a new data mapping
   */
  async createDataMapping(clientId: string, mapping: DataMappingCreate): Promise<APIResponse<DataMapping>> {
    return apiClient.post(`/api/v1/clients/${clientId}/data-mappings`, mapping);
  }

  /**
   * Update data mapping
   */
  async updateDataMapping(clientId: string, mappingId: string, updates: DataMappingUpdate): Promise<APIResponse<DataMapping>> {
    return apiClient.put(`/api/v1/clients/${clientId}/data-mappings/${mappingId}`, updates);
  }

  /**
   * Delete data mapping
   */
  async deleteDataMapping(clientId: string, mappingId: string): Promise<APIResponse<{}>> {
    return apiClient.delete(`/api/v1/clients/${clientId}/data-mappings/${mappingId}`);
  }
}

export const clientService = new ClientService();