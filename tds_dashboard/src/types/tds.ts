// TDS Core API Types

export enum EventStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  RETRY = 'retry',
  DEAD_LETTER = 'dead_letter',
}

export enum EntityType {
  PRODUCT = 'product',
  CUSTOMER = 'customer',
  INVOICE = 'invoice',
  BILL = 'bill',
  CREDIT_NOTE = 'credit_note',
  STOCK_ADJUSTMENT = 'stock_adjustment',
  PRICE_LIST = 'price_list',
  BRANCH = 'branch',
  USER = 'user',
  ORDER = 'order',
}

export enum SourceType {
  ZOHO = 'zoho',
  MANUAL = 'manual',
  SCHEDULED = 'scheduled',
  RECONCILIATION = 'reconciliation',
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy' | 'degraded';
  timestamp: string;
  uptime_seconds: number;
  database: {
    status: 'connected' | 'disconnected';
    response_time_ms?: number;
  };
  queue: {
    pending: number;
    processing: number;
    failed: number;
    completed_last_hour: number;
  };
  version: string;
}

export interface QueueStats {
  total: number;
  by_status: Record<EventStatus, number>;
  by_entity: Record<EntityType, number>;
  by_source: Record<SourceType, number>;
  oldest_pending?: {
    id: string;
    created_at: string;
    entity_type: EntityType;
    age_minutes: number;
  };
  processing_rate: {
    last_minute: number;
    last_hour: number;
    last_24_hours: number;
  };
}

export interface QueueStatsResponse {
  timestamp: string;
  total_events: number;
  by_status: Record<string, number>;
  by_entity: Record<string, number>;
  by_priority: Record<string, number>;
  oldest_pending?: {
    id: string;
    created_at: string;
    entity_type: string;
    age_minutes: number;
  } | null;
  processing_rate?: {
    last_minute: number;
    last_hour: number;
    last_24_hours: number;
  } | null;
}

export interface WebhookHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  checks: {
    database: boolean;
    queue_processing: boolean;
    recent_failures: boolean;
  };
  metrics: {
    total_webhooks_received: number;
    successful_last_hour: number;
    failed_last_hour: number;
    average_processing_time_ms: number;
    queue_backlog: number;
  };
}

export interface MetricData {
  timestamp: string;
  value: number;
}

export interface ChartDataPoint {
  time: string;
  [key: string]: string | number;
}
