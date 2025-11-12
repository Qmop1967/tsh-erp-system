// TDS Dashboard TypeScript Definitions

export type EntityType =
  | 'product'
  | 'customer'
  | 'invoice'
  | 'bill'
  | 'credit_note'
  | 'stock_adjustment'
  | 'price_list'
  | 'branch'
  | 'user'
  | 'order';

export type EventStatus =
  | 'pending'
  | 'processing'
  | 'completed'
  | 'failed'
  | 'retry'
  | 'dead_letter';

export type AlertSeverity = 'info' | 'warning' | 'error' | 'critical';

export type SyncRunStatus = 'pending' | 'running' | 'completed' | 'failed';

export type CircuitBreakerState = 'closed' | 'open' | 'half_open';

// Dashboard Overview
export interface DashboardOverview {
  health: SystemHealth;
  queue: QueueStats;
  recent_syncs: SyncRunSummary[];
  active_alerts: AlertSummary[];
  entity_status: Record<EntityType, EntitySyncStatus>;
  processing_rate: ProcessingRate;
}

// System Health
export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'critical';
  score: number; // 0-100
  uptime_seconds: number;
  last_sync_at: string | null;
  components: {
    database: ComponentHealth;
    zoho_api: ComponentHealth;
    queue: ComponentHealth;
    auto_healing: ComponentHealth;
  };
}

export interface ComponentHealth {
  status: 'healthy' | 'degraded' | 'critical';
  message?: string;
  last_check: string;
}

// Queue Statistics
export interface QueueStats {
  total: number;
  pending: number;
  processing: number;
  completed_today: number;
  failed_today: number;
  dead_letter: number;
  average_processing_time_seconds: number;
  oldest_pending_age_minutes: number | null;
}

// Sync Run Summary
export interface SyncRunSummary {
  id: number;
  run_type: string;
  entity_type: EntityType | null;
  status: SyncRunStatus;
  total_events: number;
  processed_events: number;
  failed_events: number;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
}

// Detailed Sync Run
export interface SyncRunDetail extends SyncRunSummary {
  worker_id: string | null;
  skipped_events: number;
  configuration_snapshot: Record<string, any> | null;
  error_summary: string | null;
}

// Alert
export interface AlertSummary {
  id: number;
  severity: AlertSeverity;
  title: string;
  message: string;
  triggered_at: string;
  is_active: boolean;
  acknowledged: boolean;
  resolved: boolean;
}

// Entity Sync Status
export interface EntitySyncStatus {
  entity_type: EntityType;
  last_sync_at: string | null;
  total_synced: number;
  pending_count: number;
  failed_count: number;
  success_rate: number; // 0-100
}

// Processing Rate
export interface ProcessingRate {
  current_rate: number; // items per minute
  average_rate_1h: number;
  average_rate_24h: number;
  peak_rate_24h: number;
}

// Statistics & Comparison
export interface CombinedStats {
  zoho_stats: DataSourceStats;
  local_stats: DataSourceStats;
  comparison: ComparisonResult;
  last_updated: string;
}

export interface DataSourceStats {
  total_items: number;
  total_customers: number;
  total_vendors: number;
  active_items: number;
  inactive_items: number;
  items_with_stock: number;
  total_stock_value: number;
}

export interface ComparisonResult {
  match_percentage: number;
  missing_in_local: number;
  missing_in_zoho: number;
  data_quality_score: number;
  discrepancies: Discrepancy[];
}

export interface Discrepancy {
  entity_type: EntityType;
  entity_id: string;
  field: string;
  zoho_value: any;
  local_value: any;
  severity: 'low' | 'medium' | 'high';
}

// Dead Letter Queue
export interface DeadLetterItem {
  id: number;
  entity_type: EntityType;
  source_entity_id: string;
  failure_reason: string;
  error_code: string | null;
  total_attempts: number;
  created_at: string;
  resolved: boolean;
  assigned_to: string | null;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

// Circuit Breaker
export interface CircuitBreakerStatus {
  name: string;
  state: CircuitBreakerState;
  failure_count: number;
  failure_threshold: number;
  last_failure_time: string | null;
  half_open_attempts: number;
}

// Auto-Healing Stats
export interface AutoHealingStats {
  total_healing_runs: number;
  stuck_tasks_resolved: number;
  dlq_items_retried: number;
  circuit_breakers_reset: number;
  last_run_at: string;
  next_run_at: string;
}

// Webhook Event
export interface WebhookEvent {
  id: number;
  source_type: string;
  entity_type: EntityType;
  source_entity_id: string;
  received_at: string;
  processed_at: string | null;
  signature_verified: boolean;
  validation_errors: string[] | null;
}

// API Response Wrapper
export interface APIResponse<T> {
  success: boolean;
  data: T;
  metadata?: {
    cached: boolean;
    timestamp: string;
    correlation_id: string;
  };
  error?: {
    code: string;
    message: string;
  };
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// KPI Metrics (for Admin Dashboard)
export interface KPIMetrics {
  sync_success_rate: number; // percentage
  data_accuracy: number; // percentage
  system_uptime: number; // seconds
  avg_sync_duration: number; // seconds
  critical_alerts_count: number;
  pending_queue_depth: number;
}

// Sync Trends (for charts)
export interface SyncTrend {
  timestamp: string;
  successful: number;
  failed: number;
  total_items: number;
  duration_seconds: number;
}

// Real-time Socket Events
export interface SocketEvent {
  event_type: 'sync_completed' | 'alert_created' | 'queue_updated' | 'health_changed';
  payload: any;
  timestamp: string;
}
