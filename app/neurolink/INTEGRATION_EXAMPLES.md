# TSH NeuroLink - Integration Examples

## 📘 Overview

This guide provides complete integration examples for connecting your TSH ERP modules with NeuroLink.

## 🔧 Backend Integration (Python/FastAPI)

### 1. Import the Event Emitter

```python
from app.utils.neurolink_emitter import neurolink_emitter
```

### 2. Basic Event Emission

```python
# In any TSH module handler or service
async def process_business_logic():
    # Your business logic here
    result = await do_something()

    # Emit event to NeuroLink
    success = await neurolink_emitter.emit_event(
        source_module="inventory",
        event_type="stock.low",
        payload={
            "product_id": "SKU-12345",
            "product_name": "Philips LED Bulb 9W",
            "current_stock": 10,
            "threshold": 50,
            "warehouse_id": 1
        },
        severity="warning",
        branch_id=current_user.branch_id,
        user_id=current_user.id
    )

    if success:
        logger.info("Event emitted to NeuroLink successfully")
    else:
        logger.warning("Failed to emit event to NeuroLink")
```

### 3. Price List Update Event (TDS)

```python
# In TDS price list sync handler
@event_bus.subscribe('tds.sync.completed')
async def handle_pricelist_sync_completed(event: TDSSyncCompletedEvent):
    data = event.data

    if data['entity_type'] == 'price_list':
        # Emit price list update event
        await neurolink_emitter.emit_price_list_updated(
            price_list_name="Consumer Price List",
            products_updated=data['successful'],
            sync_duration=data['duration_seconds'],
            source="zoho",
            details={
                "total_processed": data['total_processed'],
                "failed": data['failed'],
                "success_rate": (data['successful'] / data['total_processed'] * 100)
            }
        )
```

### 4. Sync Completed Event

```python
# Generic sync completion event
await neurolink_emitter.emit_sync_completed(
    entity_type="products",
    total_processed=1250,
    successful=1234,
    failed=16,
    duration=45.3
)
```

### 5. Sync Failed Event

```python
# When sync fails
await neurolink_emitter.emit_sync_failed(
    entity_type="orders",
    error_message="Connection timeout to Zoho API",
    error_code="TIMEOUT_ERROR",
    details={
        "attempted_at": datetime.utcnow().isoformat(),
        "retry_count": 3
    }
)
```

### 6. Stock Discrepancy Event

```python
# When stock mismatch detected
await neurolink_emitter.emit_stock_discrepancy(
    product_id="SKU-12345",
    product_name="Philips LED Bulb 9W",
    zoho_stock=450,
    local_stock=520,
    difference=70,
    warehouse_id=1
)
```

### 7. Image Sync Completed Event

```python
# When product images sync completes
await neurolink_emitter.emit_image_sync_completed(
    images_downloaded=45,
    images_failed=2,
    duration=120.5,
    details={
        "success_rate": 95.7,
        "storage_used_mb": 25.3
    }
)
```

### 8. Custom Event with Idempotency

```python
# Event with idempotency key to prevent duplicates
from datetime import date

await neurolink_emitter.emit_event(
    source_module="invoicing",
    event_type="invoice.overdue",
    payload={
        "invoice_id": "INV-001234",
        "customer_name": "ABC Electronics",
        "amount": 15000.00,
        "days_overdue": 15
    },
    severity="error",
    correlation_id=f"invoice_{invoice_id}",
    branch_id=branch_id
)
```

### 9. Error Handling Best Practices

```python
async def emit_event_safely(event_data: Dict[str, Any]):
    """
    Wrapper to emit events with proper error handling
    """
    try:
        success = await neurolink_emitter.emit_event(**event_data)
        if not success:
            logger.warning(f"NeuroLink event emission failed: {event_data['event_type']}")
        return success
    except Exception as e:
        logger.error(f"Error emitting NeuroLink event: {str(e)}", exc_info=True)
        # Don't let NeuroLink failures break your main business logic
        return False

# Usage
await emit_event_safely({
    "source_module": "sales",
    "event_type": "order.approved",
    "payload": {"order_id": "ORD-12345", "total": 5000.00},
    "severity": "info"
})
```

## 📱 Frontend Integration (Flutter)

### 1. Setup Firebase Messaging

```dart
// lib/services/firebase_notification_service.dart
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class FirebaseNotificationService {
  static final FirebaseNotificationService _instance =
      FirebaseNotificationService._internal();
  factory FirebaseNotificationService() => _instance;
  FirebaseNotificationService._internal();

  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();

  String? _fcmToken;
  String? get fcmToken => _fcmToken;

  Future<void> initialize() async {
    // Initialize Firebase
    await Firebase.initializeApp();

    // Request permissions
    await _requestPermissions();

    // Initialize local notifications
    await _initializeLocalNotifications();

    // Get FCM token
    _fcmToken = await _firebaseMessaging.getToken();
    print('FCM Token: $_fcmToken');

    // TODO: Send token to backend
    // await _registerTokenWithBackend(_fcmToken);

    // Configure message handlers
    _configureFCM();
  }

  Future<void> _requestPermissions() async {
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: true,
      provisional: false,
      sound: true,
    );

    print('User granted permission: ${settings.authorizationStatus}');
  }

  Future<void> _initializeLocalNotifications() async {
    const AndroidInitializationSettings androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const DarwinInitializationSettings iosSettings =
        DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const InitializationSettings initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _handleNotificationTap,
    );
  }

  void _configureFCM() {
    // Foreground messages
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('Foreground message: ${message.notification?.title}');
      _showLocalNotification(message);
    });

    // Background messages (when app is in background but running)
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('Notification tapped: ${message.notification?.title}');
      _handleNotificationTap(message.data);
    });

    // Terminated state (when app was closed)
    _firebaseMessaging.getInitialMessage().then((RemoteMessage? message) {
      if (message != null) {
        print('Launched from notification: ${message.notification?.title}');
        _handleNotificationTap(message.data);
      }
    });
  }

  Future<void> _showLocalNotification(RemoteMessage message) async {
    final severity = message.data['severity'] ?? 'info';
    final notificationId = message.data['notification_id']?.hashCode ?? 0;

    final AndroidNotificationDetails androidDetails =
        AndroidNotificationDetails(
      'tsh_${severity}',
      'TSH ${severity.toUpperCase()} Notifications',
      channelDescription: 'Notifications from TSH ERP',
      importance: _getImportance(severity),
      priority: _getPriority(severity),
      color: _getColor(severity),
    );

    const DarwinNotificationDetails iosDetails = DarwinNotificationDetails();

    final NotificationDetails details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _localNotifications.show(
      notificationId,
      message.notification?.title,
      message.notification?.body,
      details,
      payload: message.data['notification_id'],
    );
  }

  Importance _getImportance(String severity) {
    switch (severity) {
      case 'critical':
        return Importance.max;
      case 'error':
        return Importance.high;
      case 'warning':
        return Importance.defaultImportance;
      default:
        return Importance.low;
    }
  }

  Priority _getPriority(String severity) {
    switch (severity) {
      case 'critical':
        return Priority.max;
      case 'error':
        return Priority.high;
      case 'warning':
        return Priority.defaultPriority;
      default:
        return Priority.low;
    }
  }

  Color _getColor(String severity) {
    switch (severity) {
      case 'critical':
      case 'error':
        return Colors.red;
      case 'warning':
        return Colors.orange;
      default:
        return Colors.blue;
    }
  }

  void _handleNotificationTap(dynamic data) {
    // Navigate to notification screen or specific page
    if (data is Map<String, dynamic>) {
      final notificationId = data['notification_id'];
      final actionUrl = data['action_url'];

      // TODO: Implement navigation
      print('Navigate to: $actionUrl for notification: $notificationId');
    }
  }
}

// Background message handler (must be top-level function)
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('Background message: ${message.notification?.title}');
}
```

### 2. Initialize in Main

```dart
// lib/main.dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'services/firebase_notification_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase and notifications
  final notificationService = FirebaseNotificationService();
  await notificationService.initialize();

  // Set background message handler
  FirebaseMessaging.onBackgroundMessage(
    firebaseMessagingBackgroundHandler
  );

  runApp(const MyApp());
}
```

### 3. Fetch User Notifications

```dart
// lib/providers/notifications_provider.dart
import 'package:riverpod/riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class NotificationsNotifier extends StateNotifier<List<AppNotification>> {
  NotificationsNotifier() : super([]) {
    _loadNotifications();
  }

  Future<void> _loadNotifications() async {
    try {
      final response = await http.get(
        Uri.parse('$apiUrl/v1/notifications/my'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        state = data.map((json) => AppNotification.fromJson(json)).toList();
      }
    } catch (e) {
      print('Error loading notifications: $e');
    }
  }

  Future<void> markAsRead(String notificationId) async {
    try {
      await http.put(
        Uri.parse('$apiUrl/v1/notifications/$notificationId/read'),
        headers: {'Authorization': 'Bearer $token'},
      );

      // Update local state
      state = [
        for (final notification in state)
          if (notification.id == notificationId)
            notification.copyWith(isRead: true)
          else
            notification,
      ];
    } catch (e) {
      print('Error marking notification as read: $e');
    }
  }

  Future<void> acknowledge(String notificationId) async {
    try {
      await http.post(
        Uri.parse('$apiUrl/v1/notifications/$notificationId/acknowledge'),
        headers: {'Authorization': 'Bearer $token'},
      );

      // Update local state
      state = [
        for (final notification in state)
          if (notification.id == notificationId)
            notification.copyWith(
              isRead: true,
              requiresAcknowledgment: false,
            )
          else
            notification,
      ];
    } catch (e) {
      print('Error acknowledging notification: $e');
    }
  }

  Future<void> refresh() async {
    await _loadNotifications();
  }
}

final notificationsProvider =
    StateNotifierProvider<NotificationsNotifier, List<AppNotification>>((ref) {
  return NotificationsNotifier();
});
```

### 4. Notification Screen UI

```dart
// lib/screens/notifications_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class NotificationsScreen extends ConsumerStatefulWidget {
  const NotificationsScreen({super.key});

  @override
  ConsumerState<NotificationsScreen> createState() =>
      _NotificationsScreenState();
}

class _NotificationsScreenState extends ConsumerState<NotificationsScreen> {
  String _filter = 'all'; // all, unread, read

  @override
  Widget build(BuildContext context) {
    final notifications = ref.watch(notificationsProvider);
    final filteredNotifications = _filterNotifications(notifications);

    return Scaffold(
      appBar: AppBar(
        title: const Text('الإشعارات'),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.filter_list),
            onSelected: (value) => setState(() => _filter = value),
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'all', child: Text('الكل')),
              const PopupMenuItem(value: 'unread', child: Text('غير مقروء')),
              const PopupMenuItem(value: 'read', child: Text('مقروء')),
            ],
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(notificationsProvider.notifier).refresh(),
        child: filteredNotifications.isEmpty
            ? _buildEmptyState()
            : ListView.builder(
                itemCount: filteredNotifications.length,
                itemBuilder: (context, index) {
                  final notification = filteredNotifications[index];
                  return NotificationCard(
                    notification: notification,
                    onTap: () => _handleNotificationTap(notification),
                    onAcknowledge: () => _handleAcknowledge(notification.id),
                  );
                },
              ),
      ),
    );
  }

  List<AppNotification> _filterNotifications(
      List<AppNotification> notifications) {
    switch (_filter) {
      case 'unread':
        return notifications.where((n) => !n.isRead).toList();
      case 'read':
        return notifications.where((n) => n.isRead).toList();
      default:
        return notifications;
    }
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.notifications_off_outlined,
              size: 80, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text('لا توجد إشعارات',
              style: TextStyle(fontSize: 18, color: Colors.grey[600])),
        ],
      ),
    );
  }

  void _handleNotificationTap(AppNotification notification) {
    ref.read(notificationsProvider.notifier).markAsRead(notification.id);
    // Navigate to action URL or show details
  }

  void _handleAcknowledge(String notificationId) {
    ref.read(notificationsProvider.notifier).acknowledge(notificationId);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('تم تأكيد الإشعار')),
    );
  }
}
```

## 🌐 Frontend Integration (React/Next.js)

### 1. API Client Setup

```typescript
// lib/api/neurolink.ts
import axios from 'axios';

const neurolinkApi = axios.create({
  baseURL: '/api/neurolink/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
neurolinkApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default neurolinkApi;
```

### 2. Create Announcement

```typescript
// components/announcements/CreateAnnouncementForm.tsx
import { useState } from 'react';
import neurolinkApi from '@/lib/api/neurolink';

interface AnnouncementFormData {
  title: string;
  content: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  target_type: 'all' | 'roles' | 'branches';
  target_roles?: string[];
  target_branches?: number[];
  requires_acknowledgment: boolean;
  delivery_channels: string[];
  publish_at?: string;
  expires_at?: string;
}

export function CreateAnnouncementForm() {
  const [formData, setFormData] = useState<AnnouncementFormData>({
    title: '',
    content: '',
    severity: 'info',
    target_type: 'all',
    requires_acknowledgment: false,
    delivery_channels: ['in_app'],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await neurolinkApi.post('/announcements', formData);
      console.log('Announcement created:', response.data);
      // Show success message
      // Reset form or redirect
    } catch (error) {
      console.error('Error creating announcement:', error);
      // Show error message
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium">Title</label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium">Content</label>
        <textarea
          value={formData.content}
          onChange={(e) => setFormData({ ...formData, content: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300"
          rows={4}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium">Severity</label>
        <select
          value={formData.severity}
          onChange={(e) => setFormData({ ...formData, severity: e.target.value as any })}
          className="mt-1 block w-full rounded-md border-gray-300"
        >
          <option value="info">Info</option>
          <option value="warning">Warning</option>
          <option value="error">Error</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={formData.requires_acknowledgment}
            onChange={(e) => setFormData({ ...formData, requires_acknowledgment: e.target.checked })}
            className="rounded"
          />
          <span className="ml-2">Requires Acknowledgment</span>
        </label>
      </div>

      <button
        type="submit"
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Create Announcement
      </button>
    </form>
  );
}
```

### 3. List Announcements

```typescript
// components/announcements/AnnouncementsList.tsx
import { useEffect, useState } from 'react';
import neurolinkApi from '@/lib/api/neurolink';

interface Announcement {
  id: string;
  title: string;
  content: string;
  severity: string;
  status: string;
  created_at: string;
}

export function AnnouncementsList() {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnnouncements();
  }, []);

  const fetchAnnouncements = async () => {
    try {
      const response = await neurolinkApi.get('/announcements', {
        params: { status: 'published' },
      });
      setAnnouncements(response.data);
    } catch (error) {
      console.error('Error fetching announcements:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading announcements...</div>;
  }

  return (
    <div className="space-y-4">
      {announcements.map((announcement) => (
        <div
          key={announcement.id}
          className="p-4 border rounded-lg shadow-sm"
        >
          <h3 className="font-semibold text-lg">{announcement.title}</h3>
          <p className="text-gray-600 mt-2">{announcement.content}</p>
          <div className="mt-2 text-sm text-gray-500">
            {new Date(announcement.created_at).toLocaleDateString()}
          </div>
        </div>
      ))}
    </div>
  );
}
```

## 🧪 Testing Integration

### Test Event Emission

```python
# tests/test_neurolink_integration.py
import pytest
from app.utils.neurolink_emitter import neurolink_emitter

@pytest.mark.asyncio
async def test_emit_price_list_event():
    success = await neurolink_emitter.emit_price_list_updated(
        price_list_name="Test Price List",
        products_updated=100,
        sync_duration=30.5
    )
    assert success is True

@pytest.mark.asyncio
async def test_emit_sync_failed_event():
    success = await neurolink_emitter.emit_sync_failed(
        entity_type="products",
        error_message="Test error",
        error_code="TEST_ERROR"
    )
    assert success is True
```

### Test Notification Delivery

```python
# tests/test_notification_delivery.py
import pytest
from app.models import NeurolinkEvent, NeurolinkNotification

@pytest.mark.asyncio
async def test_notification_created_from_event(db_session):
    # Create test event
    event = NeurolinkEvent(
        source_module="tds",
        event_type="price_list.updated",
        severity="warning",
        payload={"price_list_name": "Consumer Price List", "products_updated": 150}
    )
    db_session.add(event)
    await db_session.commit()

    # Trigger rule engine (in real scenario, this happens automatically)
    # ...

    # Verify notification was created
    notifications = await db_session.execute(
        select(NeurolinkNotification).where(
            NeurolinkNotification.event_id == event.id
        )
    )
    assert notifications.scalar_one_or_none() is not None
```

## 📚 Additional Resources

- **API Documentation**: https://erp.tsh.sale/api/neurolink/ (when DEBUG=True)
- **Health Check**: https://erp.tsh.sale/api/neurolink/health
- **Database Schema**: See `/app/neurolink/migrations/`
- **Deployment Guide**: See `DEPLOYMENT_GUIDE.md`

## 🆘 Troubleshooting

### Events Not Creating Notifications

1. Check if NeuroLink is enabled:
```python
from app.core.config import settings
print(settings.NEUROLINK_ENABLED)  # Should be True
```

2. Verify API URL is correct:
```python
print(settings.NEUROLINK_API_URL)  # Should be http://localhost:8002 or production URL
```

3. Check notification rules:
```sql
SELECT * FROM neurolink_notification_rules
WHERE event_type_pattern = 'your.event.type'
AND is_active = true;
```

### Authentication Errors

Ensure JWT token is included in requests:
```python
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
```

### FCM Token Not Received

1. Verify Firebase configuration
2. Check app permissions for notifications
3. Ensure `google-services.json` (Android) or `GoogleService-Info.plist` (iOS) is properly configured

---

**Version**: 1.0.0
**Last Updated**: 2025-11-10
