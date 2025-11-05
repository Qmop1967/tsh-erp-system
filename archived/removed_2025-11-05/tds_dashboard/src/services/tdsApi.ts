// TDS Core API Service
import type { HealthResponse, QueueStatsResponse, WebhookHealth } from '../types/tds';

const API_BASE_URL = import.meta.env.VITE_TDS_API_URL || 'http://localhost:8001';

class TDSApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: unknown
  ) {
    super(message);
    this.name = 'TDSApiError';
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new TDSApiError(
        errorData.message || `API request failed: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof TDSApiError) {
      throw error;
    }
    throw new TDSApiError(
      error instanceof Error ? error.message : 'Unknown error occurred'
    );
  }
}

export const tdsApi = {
  // Health Check
  async getHealth(): Promise<HealthResponse> {
    return fetchApi<HealthResponse>('/health');
  },

  // Queue Statistics
  async getQueueStats(): Promise<QueueStatsResponse> {
    return fetchApi<QueueStatsResponse>('/queue/stats');
  },

  // Webhook Health
  async getWebhookHealth(): Promise<WebhookHealth> {
    return fetchApi<WebhookHealth>('/webhooks/health');
  },

  // Ping
  async ping(): Promise<{ status: string; timestamp: number }> {
    return fetchApi('/ping');
  },
};

export { TDSApiError };
