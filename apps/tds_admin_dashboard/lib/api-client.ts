import type {
  APIResponse,
  DashboardOverview,
  SyncRunDetail,
  SyncRunSummary,
  AlertSummary,
  CombinedStats,
  DeadLetterItem,
  CircuitBreakerStatus,
  AutoHealingStats,
  WebhookEvent,
  PaginatedResponse,
} from '@/types/tds';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000; // 30 seconds

// Auth Token Management
class AuthManager {
  private static TOKEN_KEY = 'tds_admin_token';
  private static REFRESH_TOKEN_KEY = 'tds_admin_refresh_token';

  static getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(this.TOKEN_KEY);
  }

  static setToken(token: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  static getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  static setRefreshToken(token: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(this.REFRESH_TOKEN_KEY, token);
  }

  static clearTokens(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }

  static isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

// API Client Class
class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    const token = AuthManager.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.status === 401) {
        // Unauthorized - clear tokens and redirect to login
        AuthManager.clearTokens();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        throw new Error('Unauthorized');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timeout');
        }
        throw error;
      }
      throw new Error('An unknown error occurred');
    } finally {
      clearTimeout(timeoutId);
    }
  }

  // Authentication
  async login(username: string, password: string): Promise<{ access_token: string; refresh_token: string }> {
    const response = await this.request<{ access_token: string; refresh_token: string }>(
      '/api/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      }
    );
    if (response.success && response.data) {
      AuthManager.setToken(response.data.access_token);
      AuthManager.setRefreshToken(response.data.refresh_token);
    }
    return response.data;
  }

  async logout(): Promise<void> {
    AuthManager.clearTokens();
  }

  // Dashboard
  async getDashboard(): Promise<DashboardOverview> {
    const response = await this.request<DashboardOverview>('/api/bff/tds/dashboard/complete');
    return response.data;
  }

  async getHealth(): Promise<any> {
    const response = await this.request<any>('/api/bff/tds/health/complete');
    return response.data;
  }

  // Sync Runs
  async getSyncRuns(params?: {
    page?: number;
    page_size?: number;
    status?: string;
    entity_type?: string;
  }): Promise<PaginatedResponse<SyncRunSummary>> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.status) queryParams.append('status', params.status);
    if (params?.entity_type) queryParams.append('entity_type', params.entity_type);

    const response = await this.request<PaginatedResponse<SyncRunSummary>>(
      `/api/bff/tds/runs?${queryParams.toString()}`
    );
    return response.data;
  }

  async getSyncRunDetail(runId: number): Promise<SyncRunDetail> {
    const response = await this.request<SyncRunDetail>(`/api/bff/tds/runs/${runId}`);
    return response.data;
  }

  async triggerStockSync(itemIds?: string[]): Promise<{ run_id: number }> {
    const response = await this.request<{ run_id: number }>('/api/bff/tds/sync/stock', {
      method: 'POST',
      body: itemIds ? JSON.stringify({ item_ids: itemIds }) : undefined,
    });
    return response.data;
  }

  // Statistics
  async getCombinedStats(): Promise<CombinedStats> {
    const response = await this.request<CombinedStats>('/api/bff/tds/stats/combined');
    return response.data;
  }

  // Alerts
  async getAlerts(params?: {
    severity?: string;
    is_active?: boolean;
  }): Promise<AlertSummary[]> {
    const queryParams = new URLSearchParams();
    if (params?.severity) queryParams.append('severity', params.severity);
    if (params?.is_active !== undefined) queryParams.append('is_active', params.is_active.toString());

    const response = await this.request<AlertSummary[]>(
      `/api/bff/tds/alerts?${queryParams.toString()}`
    );
    return response.data;
  }

  async acknowledgeAlert(alertId: number): Promise<void> {
    await this.request(`/api/bff/tds/alerts/${alertId}/acknowledge`, {
      method: 'POST',
    });
  }

  // Dead Letter Queue
  async getDeadLetterItems(params?: {
    page?: number;
    page_size?: number;
    priority?: string;
  }): Promise<PaginatedResponse<DeadLetterItem>> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.priority) queryParams.append('priority', params.priority);

    const response = await this.request<PaginatedResponse<DeadLetterItem>>(
      `/api/bff/tds/dead-letter?${queryParams.toString()}`
    );
    return response.data;
  }

  // Circuit Breakers
  async getCircuitBreakers(): Promise<CircuitBreakerStatus[]> {
    const response = await this.request<CircuitBreakerStatus[]>('/api/bff/tds/circuit-breakers');
    return response.data;
  }

  async resetCircuitBreaker(name: string): Promise<void> {
    await this.request(`/api/bff/tds/circuit-breakers/${name}/reset`, {
      method: 'POST',
    });
  }

  // Auto-Healing
  async getAutoHealingStats(): Promise<AutoHealingStats> {
    const response = await this.request<AutoHealingStats>('/api/bff/tds/auto-healing/stats');
    return response.data;
  }

  async triggerAutoHealing(): Promise<void> {
    await this.request('/api/bff/tds/auto-healing/run', {
      method: 'POST',
    });
  }

  // Webhooks
  async getRecentWebhooks(limit: number = 50): Promise<WebhookEvent[]> {
    const response = await this.request<WebhookEvent[]>(
      `/api/bff/tds/zoho/webhooks/recent?limit=${limit}`
    );
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new APIClient();
export { AuthManager };
export type { APIClient };
