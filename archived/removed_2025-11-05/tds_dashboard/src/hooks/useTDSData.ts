// React Query hooks for TDS data
import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';
import { tdsApi } from '../services/tdsApi';
import type { HealthResponse, QueueStatsResponse, WebhookHealth } from '../types/tds';

const REFRESH_INTERVAL = parseInt(
  import.meta.env.VITE_TDS_API_REFRESH_INTERVAL || '5000'
);

export function useHealth(): UseQueryResult<HealthResponse> {
  return useQuery({
    queryKey: ['tds', 'health'],
    queryFn: () => tdsApi.getHealth(),
    refetchInterval: REFRESH_INTERVAL,
    retry: 2,
  });
}

export function useQueueStats(): UseQueryResult<QueueStatsResponse> {
  return useQuery({
    queryKey: ['tds', 'queue-stats'],
    queryFn: () => tdsApi.getQueueStats(),
    refetchInterval: REFRESH_INTERVAL,
    retry: 2,
  });
}

export function useWebhookHealth(): UseQueryResult<WebhookHealth> {
  return useQuery({
    queryKey: ['tds', 'webhook-health'],
    queryFn: () => tdsApi.getWebhookHealth(),
    refetchInterval: REFRESH_INTERVAL,
    retry: 2,
  });
}

export function usePing() {
  return useQuery({
    queryKey: ['tds', 'ping'],
    queryFn: () => tdsApi.ping(),
    refetchInterval: 10000,
    retry: 1,
  });
}
