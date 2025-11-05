import api from './api';
import type {
  Notification,
  NotificationListResponse,
  NotificationStats,
  NotificationPreferences,
  NotificationType,
  NotificationPriority,
} from '../types/notification';

const BASE_URL = '/notifications';

export const notificationService = {
  // Fetch notifications
  async getNotifications(params?: {
    skip?: number;
    limit?: number;
    unread_only?: boolean;
    notification_type?: NotificationType;
    priority?: NotificationPriority;
  }): Promise<NotificationListResponse> {
    const response = await api.get(BASE_URL, { params });
    return response.data;
  },

  // Get single notification
  async getNotification(id: number): Promise<Notification> {
    const response = await api.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  // Mark as read
  async markAsRead(id: number): Promise<Notification> {
    const response = await api.put(`${BASE_URL}/${id}/read`);
    return response.data;
  },

  // Mark all as read
  async markAllAsRead(): Promise<{ count: number }> {
    const response = await api.put(`${BASE_URL}/read-all`);
    return response.data;
  },

  // Delete notification
  async deleteNotification(id: number): Promise<void> {
    await api.delete(`${BASE_URL}/${id}`);
  },

  // Archive notification
  async archiveNotification(id: number): Promise<Notification> {
    const response = await api.put(`${BASE_URL}/${id}/archive`);
    return response.data;
  },

  // Bulk operations
  async bulkMarkAsRead(notificationIds: number[]): Promise<{ count: number }> {
    const response = await api.post(`${BASE_URL}/bulk/mark-read`, {
      notification_ids: notificationIds,
    });
    return response.data;
  },

  async bulkDelete(notificationIds: number[]): Promise<{ count: number }> {
    const response = await api.post(`${BASE_URL}/bulk/delete`, {
      notification_ids: notificationIds,
    });
    return response.data;
  },

  async bulkArchive(notificationIds: number[]): Promise<{ count: number }> {
    const response = await api.post(`${BASE_URL}/bulk/archive`, {
      notification_ids: notificationIds,
    });
    return response.data;
  },

  // Statistics
  async getStats(): Promise<NotificationStats> {
    const response = await api.get(`${BASE_URL}/stats`);
    return response.data;
  },

  // Preferences
  async getPreferences(): Promise<NotificationPreferences> {
    const response = await api.get(`${BASE_URL}/preferences`);
    return response.data;
  },

  async updatePreferences(
    updates: Partial<NotificationPreferences>
  ): Promise<NotificationPreferences> {
    const response = await api.put(`${BASE_URL}/preferences`, updates);
    return response.data;
  },

  // Device token management
  async registerDeviceToken(data: {
    token: string;
    platform: 'ios' | 'android' | 'web';
    device_id?: string;
  }): Promise<{ message: string }> {
    const response = await api.post(`${BASE_URL}/device-token`, data);
    return response.data;
  },

  async unregisterDeviceToken(token: string): Promise<{ message: string }> {
    const response = await api.delete(`${BASE_URL}/device-token/${token}`);
    return response.data;
  },

  // Helper methods
  async getUnreadCount(): Promise<number> {
    const response = await this.getNotifications({ limit: 1 });
    return response.unread_count;
  },
};

export default notificationService;
