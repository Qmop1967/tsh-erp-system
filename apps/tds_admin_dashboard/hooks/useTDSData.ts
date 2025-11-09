'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { useEffect } from 'react';
import { socketManager } from '@/lib/socket';

// Query Keys
export const queryKeys = {
  dashboard: ['dashboard'] as const,
  health: ['health'] as const,
  syncRuns: (params?: any) => ['syncRuns', params] as const,
  syncRunDetail: (id: number) => ['syncRunDetail', id] as const,
  stats: ['stats'] as const,
  alerts: (params?: any) => ['alerts', params] as const,
  deadLetter: (params?: any) => ['deadLetter', params] as const,
  circuitBreakers: ['circuitBreakers'] as const,
  autoHealing: ['autoHealing'] as const,
  webhooks: (limit?: number) => ['webhooks', limit] as const,
};

// Dashboard Hook
export function useDashboard() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: () => apiClient.getDashboard(),
    refetchInterval: 30000, // 30 seconds
  });

  // Listen for real-time updates
  useEffect(() => {
    const unsubscribe = socketManager.on('queue_updated', () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
    });

    return unsubscribe;
  }, [queryClient]);

  return query;
}

// Health Hook
export function useHealth() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.health,
    queryFn: () => apiClient.getHealth(),
    refetchInterval: 15000, // 15 seconds
  });

  // Listen for real-time health changes
  useEffect(() => {
    const unsubscribe = socketManager.on('health_changed', () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.health });
    });

    return unsubscribe;
  }, [queryClient]);

  return query;
}

// Sync Runs Hook
export function useSyncRuns(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  entity_type?: string;
}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.syncRuns(params),
    queryFn: () => apiClient.getSyncRuns(params),
    refetchInterval: 30000, // 30 seconds
  });

  // Listen for sync completion
  useEffect(() => {
    const unsubscribe = socketManager.on('sync_completed', () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.syncRuns() });
    });

    return unsubscribe;
  }, [queryClient]);

  return query;
}

// Sync Run Detail Hook
export function useSyncRunDetail(runId: number | null) {
  return useQuery({
    queryKey: queryKeys.syncRunDetail(runId!),
    queryFn: () => apiClient.getSyncRunDetail(runId!),
    enabled: runId !== null,
  });
}

// Combined Stats Hook
export function useCombinedStats() {
  return useQuery({
    queryKey: queryKeys.stats,
    queryFn: () => apiClient.getCombinedStats(),
    refetchInterval: 60000, // 60 seconds
  });
}

// Alerts Hook
export function useAlerts(params?: {
  severity?: string;
  is_active?: boolean;
}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.alerts(params),
    queryFn: () => apiClient.getAlerts(params),
    refetchInterval: 15000, // 15 seconds
  });

  // Listen for new alerts
  useEffect(() => {
    const unsubscribe = socketManager.on('alert_created', () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.alerts() });
    });

    return unsubscribe;
  }, [queryClient]);

  return query;
}

// Acknowledge Alert Mutation
export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: number) => apiClient.acknowledgeAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.alerts() });
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
    },
  });
}

// Dead Letter Queue Hook
export function useDeadLetterQueue(params?: {
  page?: number;
  page_size?: number;
  priority?: string;
}) {
  return useQuery({
    queryKey: queryKeys.deadLetter(params),
    queryFn: () => apiClient.getDeadLetterItems(params),
    refetchInterval: 30000, // 30 seconds
  });
}

// Circuit Breakers Hook
export function useCircuitBreakers() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.circuitBreakers,
    queryFn: () => apiClient.getCircuitBreakers(),
    refetchInterval: 30000, // 30 seconds
  });

  // Listen for circuit breaker state changes
  useEffect(() => {
    const unsubscribe = socketManager.on('circuit_breaker_state_changed', () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.circuitBreakers });
    });

    return unsubscribe;
  }, [queryClient]);

  return query;
}

// Reset Circuit Breaker Mutation
export function useResetCircuitBreaker() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (name: string) => apiClient.resetCircuitBreaker(name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.circuitBreakers });
    },
  });
}

// Auto-Healing Stats Hook
export function useAutoHealingStats() {
  return useQuery({
    queryKey: queryKeys.autoHealing,
    queryFn: () => apiClient.getAutoHealingStats(),
    refetchInterval: 60000, // 60 seconds
  });
}

// Trigger Auto-Healing Mutation
export function useTriggerAutoHealing() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiClient.triggerAutoHealing(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.autoHealing });
    },
  });
}

// Trigger Stock Sync Mutation
export function useTriggerStockSync() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (itemIds?: string[]) => apiClient.triggerStockSync(itemIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.syncRuns() });
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
    },
  });
}

// Recent Webhooks Hook
export function useRecentWebhooks(limit: number = 50) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.webhooks(limit),
    queryFn: () => apiClient.getRecentWebhooks(limit),
    refetchInterval: 30000, // 30 seconds
  });

  // Listen for new webhooks
  useEffect(() => {
    const unsubscribe = socketManager.on('webhook_received', () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.webhooks() });
    });

    return unsubscribe;
  }, [queryClient]);

  return query;
}
