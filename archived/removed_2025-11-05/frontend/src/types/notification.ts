export enum NotificationType {
  // Inventory notifications
  LOW_STOCK = 'low_stock',
  OUT_OF_STOCK = 'out_of_stock',
  STOCK_MOVEMENT = 'stock_movement',
  STOCK_ADJUSTMENT = 'stock_adjustment',

  // Sales notifications
  NEW_ORDER = 'new_order',
  ORDER_CONFIRMED = 'order_confirmed',
  ORDER_SHIPPED = 'order_shipped',
  ORDER_DELIVERED = 'order_delivered',
  ORDER_CANCELLED = 'order_cancelled',

  // Purchase notifications
  PURCHASE_ORDER_CREATED = 'purchase_order_created',
  PURCHASE_ORDER_APPROVED = 'purchase_order_approved',
  PURCHASE_ORDER_RECEIVED = 'purchase_order_received',

  // Financial notifications
  INVOICE_CREATED = 'invoice_created',
  INVOICE_PAID = 'invoice_paid',
  INVOICE_OVERDUE = 'invoice_overdue',
  PAYMENT_RECEIVED = 'payment_received',

  // HR notifications
  LEAVE_REQUEST = 'leave_request',
  LEAVE_APPROVED = 'leave_approved',
  LEAVE_REJECTED = 'leave_rejected',
  TIMESHEET_REMINDER = 'timesheet_reminder',

  // System notifications
  SYSTEM_ALERT = 'system_alert',
  SYSTEM_UPDATE = 'system_update',
  BACKUP_COMPLETE = 'backup_complete',
  BACKUP_FAILED = 'backup_failed',

  // User notifications
  USER_MENTIONED = 'user_mentioned',
  TASK_ASSIGNED = 'task_assigned',
  APPROVAL_REQUEST = 'approval_request',
  MESSAGE_RECEIVED = 'message_received',

  // Custom
  CUSTOM = 'custom',
}

export enum NotificationPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export interface NotificationAction {
  label: string;
  url: string;
  style?: 'primary' | 'secondary' | 'danger';
}

export interface Notification {
  id: number;
  user_id: number;
  tenant_id?: number;
  type: NotificationType;
  priority: NotificationPriority;
  title: string;
  message: string;

  // Rich content
  image_url?: string;
  icon?: string;
  color?: string;

  // Actions
  action_url?: string;
  action_label?: string;
  actions?: NotificationAction[];

  // Metadata
  meta_data?: Record<string, any>;

  // Status
  is_read: boolean;
  is_archived: boolean;
  read_at?: string;

  // Delivery
  channels: string[];
  sent_via?: string[];
  delivery_status?: Record<string, string>;

  // Timestamps
  created_at: string;
  updated_at: string;
  expires_at?: string;

  // Related entity
  related_entity_type?: string;
  related_entity_id?: number;
}

export interface NotificationListResponse {
  notifications: Notification[];
  total: number;
  unread_count: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface NotificationStats {
  total_notifications: number;
  unread_count: number;
  read_count: number;
  archived_count: number;
  by_priority: Record<string, number>;
  by_type: Record<string, number>;
  recent_activity: Array<Record<string, any>>;
}

export interface NotificationPreferences {
  id: number;
  user_id: number;
  enabled: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  enable_in_app: boolean;
  enable_push: boolean;
  enable_email: boolean;
  enable_sms: boolean;
  type_preferences?: Record<string, Record<string, boolean>>;
  min_priority: NotificationPriority;
  fcm_tokens?: string[];
  apns_tokens?: string[];
  email_address?: string;
  email_digest_enabled: boolean;
  email_digest_frequency: string;
  created_at: string;
  updated_at: string;
}
