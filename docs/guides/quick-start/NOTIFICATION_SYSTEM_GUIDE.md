# TSH ERP Ecosystem - Unified Notification System

## Overview

The TSH ERP Ecosystem now features a comprehensive, enterprise-grade unified notification system that provides real-time notifications across all platforms (web, mobile) with the following features:

- **Multi-channel delivery**: In-app, push notifications, email, SMS, WebSocket
- **20+ notification types**: Covering all ERP modules (Inventory, Sales, Financial, HR, System)
- **4 priority levels**: Low, Medium, High, Critical
- **Rich content**: Images, icons, colors, action buttons
- **User preferences**: Quiet hours, channel-specific settings, priority filtering
- **Real-time updates**: WebSocket integration for instant notifications
- **Template system**: Reusable notification templates with variable substitution
- **Bulk operations**: Mark as read, delete, archive multiple notifications
- **Statistics**: Comprehensive notification analytics

## Architecture

### Backend (Python/FastAPI)
- **Database Models**: 5 tables (notifications, templates, preferences, groups, logs)
- **REST API**: 20+ endpoints for complete CRUD operations
- **WebSocket**: Real-time notification delivery
- **Service Layer**: Business logic for notification management
- **Alembic Migrations**: Database schema versioning

### Mobile (Flutter/Dart)
- **Firebase Cloud Messaging**: Push notification delivery
- **Beautiful UI**: Notification center with tabs, badges, swipe-to-delete
- **Local notifications**: In-app notification display
- **Token management**: FCM token registration with backend
- **Priority-based styling**: Color-coded notifications

### Web (React/TypeScript)
- **Material-UI components**: Professional notification center
- **WebSocket hook**: Real-time notification updates
- **NotificationBell**: Badge with unread count
- **Auto-refresh**: Periodic polling for new notifications
- **Responsive design**: Mobile-friendly drawer interface

## Database Schema

### notifications table
```sql
- id: Primary key
- user_id: Foreign key to users
- tenant_id: Foreign key to tenants (optional, for multi-tenancy)
- type: NotificationType enum (low_stock, new_order, invoice_created, etc.)
- priority: NotificationPriority enum (low, medium, high, critical)
- title: Short notification title
- message: Full notification message
- image_url: Optional image
- icon: Optional icon name
- color: Optional color hex code
- action_url: Deep link URL
- action_label: Button label
- actions: JSON array of action buttons
- meta_data: JSON object for additional data
- is_read: Boolean flag
- is_archived: Boolean flag
- read_at: Timestamp when read
- channels: JSON array of delivery channels
- sent_via: JSON array of successful delivery channels
- delivery_status: JSON object with delivery status per channel
- created_at, updated_at, expires_at: Timestamps
- related_entity_type, related_entity_id: Link to related entities
```

### notification_templates table
```sql
- id: Primary key
- name: Unique template name
- type: NotificationType
- priority: NotificationPriority
- title_template: Title with {{variables}}
- message_template: Message with {{variables}}
- icon, color: Default styling
- action_url_template: URL with {{variables}}
- default_channels: JSON array of channels
- variables: JSON array of required variables
- is_active: Boolean flag
```

### notification_preferences table
```sql
- id: Primary key
- user_id: Foreign key to users
- enabled: Global notification toggle
- quiet_hours_enabled: Boolean flag
- quiet_hours_start, quiet_hours_end: Time strings
- enable_in_app, enable_push, enable_email, enable_sms: Channel toggles
- type_preferences: JSON object with per-type channel settings
- min_priority: Minimum priority to receive
- fcm_tokens, apns_tokens: Device tokens
- email_address: Email for notifications
- email_digest_enabled, email_digest_frequency: Email digest settings
```

## API Endpoints

### Notification Management
- `GET /api/v1/notifications` - Get user notifications with filters
- `GET /api/v1/notifications/{id}` - Get single notification
- `PUT /api/v1/notifications/{id}/read` - Mark as read
- `PUT /api/v1/notifications/read-all` - Mark all as read
- `DELETE /api/v1/notifications/{id}` - Delete notification
- `PUT /api/v1/notifications/{id}/archive` - Archive notification

### Bulk Operations
- `POST /api/v1/notifications/bulk/mark-read` - Bulk mark as read
- `POST /api/v1/notifications/bulk/delete` - Bulk delete
- `POST /api/v1/notifications/bulk/archive` - Bulk archive

### Statistics & Preferences
- `GET /api/v1/notifications/stats` - Get notification statistics
- `GET /api/v1/notifications/preferences` - Get user preferences
- `PUT /api/v1/notifications/preferences` - Update preferences

### Device Tokens
- `POST /api/v1/notifications/device-token` - Register device token
- `DELETE /api/v1/notifications/device-token/{token}` - Unregister token

### WebSocket
- `WS /api/v1/notifications/ws/{user_id}` - Real-time notifications

## Usage Examples

### Backend - Creating a Notification

```python
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType, NotificationPriority

# Create a low stock notification
notification = NotificationService.create_notification(
    db=db,
    user_id=user_id,
    notification_type=NotificationType.LOW_STOCK,
    priority=NotificationPriority.HIGH,
    title="Low Stock Alert",
    message="Product 'Premium Widget' is running low on stock (5 units remaining)",
    action_url="/inventory/products/123",
    action_label="View Product",
    meta_data={"product_id": 123, "current_stock": 5, "min_stock": 10},
    channels=["in_app", "push", "email"]
)
```

### Backend - Using Templates

```python
# Create notification from template
notification = NotificationService.create_from_template(
    db=db,
    template_name="low_stock_alert",
    user_id=user_id,
    variables={
        "product_name": "Premium Widget",
        "current_stock": 5,
        "min_stock": 10,
        "product_id": 123
    }
)
```

### Mobile - Initializing Firebase Messaging

```dart
import 'package:tsh_inventory_app_new/services/firebase_messaging_service.dart';

// In main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase Messaging
  final firebaseMessaging = FirebaseMessagingService();
  await firebaseMessaging.initialize();

  runApp(MyApp());
}
```

### Mobile - Displaying Notification Center

```dart
import 'package:tsh_inventory_app_new/screens/notification_center_screen.dart';

// Navigate to notification center
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => const NotificationCenterScreen(),
  ),
);
```

### Web - Using NotificationBell Component

```tsx
import { NotificationBell } from '@/components/notifications';

// In your header/layout component
<NotificationBell
  autoRefresh={true}
  refreshInterval={30000} // 30 seconds
/>
```

### Web - Using WebSocket for Real-time Updates

```tsx
import useNotificationWebSocket from '@/hooks/useNotificationWebSocket';

function MyComponent() {
  const { isConnected } = useNotificationWebSocket({
    userId: currentUser.id,
    onNotification: (notification) => {
      console.log('New notification:', notification);
      // Show toast, play sound, etc.
    },
    onConnect: () => console.log('WebSocket connected'),
    onDisconnect: () => console.log('WebSocket disconnected'),
  });

  return <div>WebSocket status: {isConnected ? 'Connected' : 'Disconnected'}</div>;
}
```

## Notification Types

### Inventory
- `LOW_STOCK` - Product stock below minimum level
- `OUT_OF_STOCK` - Product completely out of stock
- `STOCK_MOVEMENT` - Stock transfer or movement
- `STOCK_ADJUSTMENT` - Manual stock adjustment

### Sales
- `NEW_ORDER` - New sales order created
- `ORDER_CONFIRMED` - Order confirmed by customer
- `ORDER_SHIPPED` - Order shipped
- `ORDER_DELIVERED` - Order delivered
- `ORDER_CANCELLED` - Order cancelled

### Purchase
- `PURCHASE_ORDER_CREATED` - New purchase order
- `PURCHASE_ORDER_APPROVED` - PO approved
- `PURCHASE_ORDER_RECEIVED` - PO received

### Financial
- `INVOICE_CREATED` - New invoice
- `INVOICE_PAID` - Invoice paid
- `INVOICE_OVERDUE` - Invoice overdue
- `PAYMENT_RECEIVED` - Payment received

### HR
- `LEAVE_REQUEST` - New leave request
- `LEAVE_APPROVED` - Leave approved
- `LEAVE_REJECTED` - Leave rejected
- `TIMESHEET_REMINDER` - Timesheet submission reminder

### System
- `SYSTEM_ALERT` - System alert or warning
- `SYSTEM_UPDATE` - System update available
- `BACKUP_COMPLETE` - Backup completed successfully
- `BACKUP_FAILED` - Backup failed

### User
- `USER_MENTIONED` - User mentioned in comment
- `TASK_ASSIGNED` - Task assigned to user
- `APPROVAL_REQUEST` - Approval request
- `MESSAGE_RECEIVED` - New message

## Configuration

### Environment Variables

```bash
# Backend
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Firebase (Mobile)
# Configure in Firebase Console and download google-services.json / GoogleService-Info.plist
```

### Firebase Setup for Mobile

1. Create Firebase project at https://console.firebase.google.com
2. Add iOS app with bundle ID: `com.tsh.inventoryapp`
3. Download `GoogleService-Info.plist` to `ios/Runner/`
4. Add Android app with package name: `com.tsh.inventoryapp`
5. Download `google-services.json` to `android/app/`
6. Enable Cloud Messaging in Firebase Console

## Testing

### Backend Tests

```bash
# Create test notification
curl -X POST http://localhost:8000/api/v1/notifications \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "low_stock",
    "priority": "high",
    "title": "Test Notification",
    "message": "This is a test notification",
    "channels": ["in_app"]
  }'

# Get notifications
curl http://localhost:8000/api/v1/notifications?limit=10 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get unread count
curl http://localhost:8000/api/v1/notifications/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Mobile Tests

```dart
// Test notification service
final notificationService = NotificationService();
final notifications = await notificationService.getNotifications(limit: 10);
print('Notifications: ${notifications.length}');

// Test FCM
final firebaseMessaging = FirebaseMessagingService();
await firebaseMessaging.initialize();
print('FCM Token: ${firebaseMessaging.fcmToken}');
```

### Web Tests

```bash
# Open browser console and test
// Manually trigger notification fetch
notificationService.getNotifications({ limit: 10 })
  .then(response => console.log('Notifications:', response));

// Test WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/notifications/ws/1');
ws.onmessage = (event) => console.log('Notification:', JSON.parse(event.data));
```

## Files Created/Modified

### Backend
- `app/models/notification.py` - Database models
- `app/schemas/notification.py` - Pydantic schemas
- `app/services/notification_service.py` - Business logic
- `app/routers/notifications.py` - API endpoints
- `app/main.py` - Router registration
- `database/alembic/versions/f7145b8f57e0_add_unified_notification_system_tables.py` - Migration

### Mobile (Flutter)
- `lib/models/notification_models.dart` - Dart models
- `lib/services/notification_service.dart` - API service
- `lib/services/firebase_messaging_service.dart` - FCM integration
- `lib/screens/notification_center_screen.dart` - Notification center UI
- `lib/screens/enhanced_dashboard_screen.dart` - Dashboard with bell icon
- `pubspec.yaml` - Added firebase_core, firebase_messaging, intl

### Frontend (React)
- `src/types/notification.ts` - TypeScript types
- `src/services/notificationService.ts` - API service
- `src/components/notifications/NotificationCenter.tsx` - Notification drawer
- `src/components/notifications/NotificationBell.tsx` - Bell icon with badge
- `src/components/notifications/index.ts` - Exports
- `src/hooks/useNotificationWebSocket.ts` - WebSocket hook
- `src/components/layout/Header.tsx` - Integrated NotificationBell
- `package.json` - Added date-fns

## Performance Considerations

1. **Database Indexes**: All frequently queried columns are indexed (user_id, type, priority, is_read)
2. **Pagination**: All list endpoints support skip/limit pagination
3. **WebSocket**: Connection pooling with automatic reconnection
4. **Caching**: Frontend caches notification count, auto-refreshes every 30 seconds
5. **Bulk Operations**: Efficient bulk mark-as-read, delete, archive
6. **Expiration**: Notifications auto-expire based on expires_at field
7. **Archiving**: Old notifications can be archived to reduce query load

## Security

1. **Authentication**: All endpoints require JWT Bearer token
2. **Authorization**: Users can only access their own notifications
3. **Multi-tenancy**: Optional tenant_id for organization isolation
4. **Input Validation**: Pydantic schemas validate all inputs
5. **SQL Injection**: SQLAlchemy ORM prevents SQL injection
6. **XSS Protection**: Frontend sanitizes notification content
7. **CORS**: Configured in FastAPI for allowed origins

## Future Enhancements

1. **Push Notification Scheduling**: Schedule notifications for specific times
2. **Notification Groups**: Group related notifications
3. **Rich Push**: Images, videos in push notifications
4. **Sound & Vibration**: Customizable notification sounds
5. **Do Not Disturb**: Respect system DND settings
6. **Notification History**: Separate archive view
7. **Export**: Export notification history as CSV/PDF
8. **Analytics**: Dashboard for notification engagement metrics
9. **A/B Testing**: Test different notification templates
10. **Rate Limiting**: Prevent notification spam

## Support

For issues or questions:
- Backend API: Check logs at `app.log`
- Mobile: Check console output in Xcode/Android Studio
- Web: Check browser console for errors
- Database: Check Alembic migration status with `alembic current`

## License

This notification system is part of the TSH ERP Ecosystem and follows the project's license terms.

---

**Last Updated**: 2025-10-24
**Version**: 1.0.0
**Author**: TSH ERP Development Team
