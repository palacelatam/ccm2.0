/**
 * Client Service for API communication with backend
 */

import { auth } from '../config/firebase';

// API Response types
interface APIResponse<T> {
  success: boolean;
  data: T;
  message: string;
  error_code?: string;
}

// Trade-related types
export interface UnmatchedTrade {
  id: string;
  tradeNumber: string;
  counterpartyName: string;
  productType: string;
  tradeDate: string;
  valueDate: string;
  direction: string;
  currency1: string;
  quantityCurrency1: number;
  currency2: string;
  forwardPrice: number;
  maturityDate: string;
  fixingReference: string;
  settlementType: string;
  settlementCurrency: string;
  paymentDate: string;
  counterpartyPaymentMethod: string;
  ourPaymentMethod: string;
  status: string;
  createdAt: string;
}

export interface EmailConfirmation {
  id: string;
  matchId?: string;  // Optional - only present for matched emails
  emailSender: string;
  emailDate: string;
  emailTime: string;
  emailSubject: string;
  emailBody: string;
  bankTradeNumber: string;
  llmExtractedData?: any;
  status: string;
  createdAt: string;
}

export interface TradeMatch {
  id: string;
  matchId: string;  // Unique identifier for linking grids
  tradeId: string;
  emailId: string;
  confidenceScore: number;
  matchReasons: string[];
  discrepancies: any[];
  status: string;
  createdAt: string;
}

export interface UploadResult {
  upload_session_id: string;
  file_name: string;
  file_size: number;
  records_processed: number;
  message: string;
  // Additional fields for email uploads
  email_id?: string;
  trades_extracted?: number;
  confirmation_detected?: boolean;
  matches_found?: number;
  duplicates_found?: number;
  counterparty_name?: string;
  matched_trade_numbers?: string[];
}

export interface ProcessMatchesResult {
  unmatched_trades: number;
  unmatched_emails: number;
  matches_found: number;
  confidence_scores: number[];
  message: string;
}

class ClientService {
  private baseURL = '/api/v1/clients';

  /**
   * Get authentication token from Firebase
   */
  private async getAuthToken(): Promise<string> {
    const user = auth.currentUser;
    if (!user) {
      throw new Error('User not authenticated');
    }
    return await user.getIdToken();
  }

  /**
   * Make authenticated API request
   */
  private async makeRequest<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    const token = await this.getAuthToken();
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.message || errorMessage;
      } catch {
        // Use default error message if JSON parsing fails
      }
      
      throw new Error(errorMessage);
    }

    return await response.json();
  }

  // ========== Trade Management Methods ==========

  /**
   * Get all unmatched trades for a client
   */
  async getUnmatchedTrades(clientId: string): Promise<UnmatchedTrade[]> {
    const response = await this.makeRequest<UnmatchedTrade[]>(
      `${this.baseURL}/${clientId}/unmatched-trades`
    );
    return response.data;
  }

  /**
   * Get all email confirmations for a client
   */
  async getEmailConfirmations(clientId: string): Promise<EmailConfirmation[]> {
    const response = await this.makeRequest<EmailConfirmation[]>(
      `${this.baseURL}/${clientId}/email-confirmations`
    );
    return response.data;
  }

  /**
   * Get all trade matches for a client
   */
  async getTradeMatches(clientId: string): Promise<TradeMatch[]> {
    const response = await this.makeRequest<TradeMatch[]>(
      `${this.baseURL}/${clientId}/matches`
    );
    return response.data;
  }

  /**
   * Get matched trades with enriched match information
   */
  async getMatchedTrades(clientId: string): Promise<any[]> {
    const response = await this.makeRequest<any[]>(
      `${this.baseURL}/${clientId}/matched-trades`
    );
    return response.data;
  }

  /**
   * Get all email confirmations with extracted trade data
   */
  async getAllEmailConfirmations(clientId: string): Promise<any[]> {
    const response = await this.makeRequest<any[]>(
      `${this.baseURL}/${clientId}/all-email-confirmations`
    );
    return response.data;
  }

  /**
   * Upload trade file (Excel/CSV)
   */
  async uploadTradeFile(clientId: string, file: File): Promise<UploadResult> {
    return this.uploadTradeFileWithOverwrite(clientId, file, false);
  }

  /**
   * Upload trade file with overwrite option
   */
  async uploadTradeFileWithOverwrite(clientId: string, file: File, overwrite: boolean = false): Promise<UploadResult> {
    const token = await this.getAuthToken();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('overwrite', overwrite.toString());

    const response = await fetch(`${this.baseURL}/${clientId}/upload-trades`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.message || errorJson.detail || errorMessage;
      } catch {
        // Use default error message
      }
      
      throw new Error(errorMessage);
    }

    const result: APIResponse<UploadResult> = await response.json();
    return result.data;
  }

  /**
   * Upload email file (.msg/.pdf)
   */
  async uploadEmailFile(clientId: string, file: File): Promise<UploadResult> {
    const token = await this.getAuthToken();
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/${clientId}/upload-emails`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.message || errorMessage;
      } catch {
        // Use default error message
      }
      
      throw new Error(errorMessage);
    }

    const result: APIResponse<UploadResult> = await response.json();
    return result.data;
  }

  /**
   * Delete all unmatched trades for a client
   */
  async deleteAllUnmatchedTrades(clientId: string): Promise<{trades_deleted: number, message: string}> {
    const response = await this.makeRequest<{trades_deleted: number, message: string}>(
      `${this.baseURL}/${clientId}/unmatched-trades`,
      { method: 'DELETE' }
    );
    return response.data;
  }

  /**
   * Process matches between trades and emails
   */
  async processMatches(clientId: string): Promise<ProcessMatchesResult> {
    const response = await this.makeRequest<ProcessMatchesResult>(
      `${this.baseURL}/${clientId}/process-matches`,
      { method: 'POST' }
    );
    return response.data;
  }

  // ========== Utility Methods ==========

  /**
   * Format currency amount for display
   */
  static formatCurrency(amount: number, locale: string = 'es-CL'): string {
    return new Intl.NumberFormat(locale, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  }

  /**
   * Format date for display
   */
  static formatDate(dateString: string, locale: string = 'es-CL'): string {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString(locale);
    } catch {
      return dateString;
    }
  }

  /**
   * Get status display class for styling
   */
  static getStatusClass(status: string): string {
    switch (status.toLowerCase()) {
      case 'unmatched':
        return 'status-unmatched';
      case 'matched':
        return 'status-matched';
      case 'confirmed':
        return 'status-confirmed';
      case 'review_needed':
        return 'status-review-needed';
      default:
        return 'status-default';
    }
  }
}

// Export singleton instance
export const clientService = new ClientService();
// Export class for static methods
export { ClientService };
export default clientService;