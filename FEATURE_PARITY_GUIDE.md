# TSH ERP Feature Parity Guide

## Architecture Overview

Each React Admin module corresponds to multiple Flutter apps that share the same database tables. The React Admin module provides **centralized oversight and control** over all the Flutter apps in its domain.

```
React Module          Flutter Apps Sharing Same DB          Database Tables
─────────────────────────────────────────────────────────────────────────────
📊 ACCOUNTING    ←→   • Accounting App                   →  journals, journal_entries,
   Module                                                   accounts, ledger

💰 SALES         ←→   • Field Sales Rep App             →  clients, orders, products,
   Module            • Partner Network App                 retailers, partners,
                     • Retailer App                        consumers, transactions,
                     • Consumer App                        cart_items, visits
                     • Client Management App

📦 INVENTORY     ←→   • Warehouse App                    →  products, inventory,
   Module            • Stock Management App                 warehouses, transfers,
                                                           stock_movements

🔧 AFTER-SALES   ←→   • Technician Service App          →  service_requests, returns,
   Module            • Maintenance App                     inspections, warranty,
                                                           maintenance_jobs

👥 HR            ←→   • Employee Self-Service App       →  employees, attendance,
   Module            • Time Tracking App                   payroll, leaves
```

---

## Feature Parity Rules

### Rule 1: Flutter App Features → React Admin Module
**When you add a feature to ANY Flutter app, you MUST add it to the corresponding React Admin module.**

**Example - Sales Module:**
```
If Field Sales Rep App gets "Create Visit Report" feature:
  ✅ Add "View All Visit Reports" to React Admin Sales Module
  ✅ Add "Visit Analytics" dashboard to React Admin
  ✅ Add "Export Visit Reports" to React Admin
  ✅ Enable WebSocket real-time updates when visits created
```

### Rule 2: React Admin = Superset
**React Admin module contains ALL features from ALL its Flutter apps PLUS admin-only features.**

**Admin-Only Features:**
- User management (create users for Flutter apps)
- Role & permissions management
- System configuration
- Advanced analytics & reports
- Bulk operations
- Data import/export
- Audit logs
- Period closing/locking

### Rule 3: Shared Database = Instant Sync
**All apps write to same tables, WebSocket broadcasts changes.**

**Implementation:**
```python
# Backend - When Flutter app creates record
@router.post("/orders")
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # 1. Save to database
    new_order = service.create_order(order)

    # 2. Broadcast to React Admin via WebSocket
    await sales_ws_manager.broadcast_order_created({
        "id": new_order.id,
        "customer": new_order.customer_name,
        "total": float(new_order.total),
        "source_app": "field_sales_rep"  # Track which app created it
    })

    return new_order
```

---

## Module-to-Apps Mapping

### 1. 📊 ACCOUNTING MODULE

**React Admin Features:**
```
✅ Dashboard
   - Total Assets/Liabilities/Equity
   - Net Profit/Loss
   - Cash Flow Summary
   - Account Balances

✅ Chart of Accounts Management
   - Create/Edit/Delete accounts
   - Account hierarchy
   - Account types & categories

✅ Journal Entries
   - View all entries from ALL sources
   - Create/Edit/Post/Reverse entries
   - Approval workflows
   - Entry templates

✅ Financial Reports
   - Balance Sheet
   - Income Statement
   - Trial Balance
   - Cash Flow Statement
   - Custom reports

✅ Period Management
   - Create fiscal years
   - Manage accounting periods
   - Period closing
   - Year-end closing

✅ Administration
   - User permissions
   - Journal templates
   - Approval workflows
   - Audit logs
```

**Flutter Accounting App Features:**
```
✅ Mobile Dashboard (subset of React)
✅ Create Journal Entries (mobile-friendly)
✅ View Recent Entries
✅ Account Search & Selection
✅ Photo Attachments for entries
✅ Offline support
```

**Database Tables:**
- `accounting_currencies`
- `accounting_exchange_rates`
- `accounting_chart_of_accounts`
- `accounting_accounts`
- `accounting_journals`
- `accounting_journal_entries`
- `accounting_journal_entry_lines`
- `accounting_ledger_entries`
- `accounting_fiscal_years`
- `accounting_periods`

---

### 2. 💰 SALES MODULE

**React Admin Features:**
```
✅ Unified Sales Dashboard
   - Total sales from ALL apps
   - Sales by channel (Field, Partner, Retailer, Consumer)
   - Top products across all channels
   - Revenue trends
   - Sales targets vs actuals

✅ Clients Management
   - ALL clients from all apps
   - Client categories & segments
   - Credit limits & payment terms
   - Purchase history
   - Client analytics

✅ Orders Management
   - Orders from Field Sales Rep App
   - Orders from Partner Network App
   - Orders from Retailer App
   - Orders from Consumer App
   - Order status tracking
   - Fulfillment management

✅ Products Management
   - Product catalog
   - Pricing by channel
   - Inventory levels
   - Product performance analytics

✅ Partners & Retailers
   - Partner network hierarchy
   - Retailer management
   - Commission tracking
   - Performance analytics

✅ Sales Team Management
   - Sales rep performance
   - Territory management
   - Target setting
   - Commission calculations

✅ Reports & Analytics
   - Sales by product/category/region
   - Sales rep performance
   - Partner network performance
   - Retailer performance
   - Consumer behavior analytics
   - Forecasting & trends
```

**Flutter Field Sales Rep App Features:**
```
✅ My Dashboard (personal performance)
✅ My Clients (assigned clients only)
✅ Create Orders
✅ Client Visit Tracking
✅ Product Catalog (view)
✅ My Targets & Achievements
✅ Route Planning
✅ Offline Order Creation
```

**Flutter Partner Network App Features:**
```
✅ Partner Dashboard (network performance)
✅ My Retailers (managed retailers only)
✅ Onboard New Retailers
✅ View Network Orders
✅ Commission Tracking
✅ Training Materials
```

**Flutter Retailer App Features:**
```
✅ Retailer Dashboard (store performance)
✅ Browse Products
✅ Create Purchase Orders
✅ Track Deliveries
✅ View Sales History
✅ Inventory Management (store level)
✅ Promotions & Offers
```

**Flutter Consumer App Features:**
```
✅ Product Catalog & Search
✅ Shopping Cart
✅ Create Orders
✅ Track Orders
✅ Wishlist
✅ Reviews & Ratings
✅ Loyalty Points
```

**Flutter Client Management App Features:**
```
✅ Client Profile
✅ Order History
✅ Pending Orders
✅ Invoices & Payments
✅ Support Tickets
✅ Loyalty Program
```

**Database Tables:**
```
Sales Core:
- `sales_clients`
- `sales_orders`
- `sales_order_items`
- `sales_products`
- `sales_categories`
- `sales_pricing`

Partners & Retailers:
- `sales_partners`
- `sales_retailers`
- `sales_partner_retailers` (relationship)
- `sales_commissions`

Sales Team:
- `sales_reps`
- `sales_territories`
- `sales_targets`
- `sales_visits`

Consumers:
- `sales_consumers`
- `sales_cart`
- `sales_wishlist`
- `sales_reviews`
- `sales_loyalty_points`
```

---

### 3. 📦 INVENTORY MODULE

**React Admin Features:**
```
✅ Inventory Dashboard
   - Total stock value
   - Low stock alerts
   - Stock by warehouse
   - Inventory turnover

✅ Products Management
   - Product master data
   - SKU management
   - Product variants
   - Product images & specs

✅ Warehouses
   - Warehouse management
   - Location tracking
   - Bin management

✅ Stock Movements
   - Transfers between warehouses
   - Stock adjustments
   - Cycle counts
   - Movement history

✅ Procurement
   - Purchase orders
   - Supplier management
   - Receiving
   - GRN (Goods Receipt Notes)

✅ Reports
   - Stock valuation
   - Inventory aging
   - Movement reports
   - ABC analysis
```

**Flutter Warehouse App Features:**
```
✅ Warehouse Dashboard
✅ Receive Goods
✅ Pick & Pack Orders
✅ Stock Transfer
✅ Cycle Counting
✅ Barcode Scanning
```

**Database Tables:**
- `inventory_products`
- `inventory_warehouses`
- `inventory_locations`
- `inventory_stock`
- `inventory_movements`
- `inventory_transfers`
- `inventory_adjustments`

---

### 4. 🔧 AFTER-SALES OPERATIONS MODULE

**React Admin Features:**
```
✅ ASO Dashboard
   - Pending service requests
   - Maintenance jobs in progress
   - Return requests
   - Warranty claims

✅ Service Requests Management
   - All requests from all channels
   - Assignment to technicians
   - Status tracking
   - Resolution time analytics

✅ Returns Management
   - Return requests
   - Inspection results
   - Decision tracking (refund/replace/repair)
   - Return analytics

✅ Maintenance Jobs
   - Scheduled maintenance
   - Job assignment
   - Parts management
   - Job completion tracking

✅ Warranty Management
   - Warranty registration
   - Claims processing
   - Warranty analytics

✅ Technician Management
   - Technician scheduling
   - Performance tracking
   - Skills management

✅ Reports
   - Service level metrics
   - Return rate analysis
   - Technician performance
   - Warranty cost analysis
```

**Flutter Technician Service App Features:**
```
✅ My Jobs Dashboard
✅ View Assigned Jobs
✅ Job Check-in/Check-out
✅ Update Job Status
✅ Parts Used Tracking
✅ Customer Signature Capture
✅ Photo Documentation
✅ Offline Mode
```

**Database Tables:**
- `aso_service_requests`
- `aso_returns`
- `aso_inspections`
- `aso_maintenance_jobs`
- `aso_warranty`
- `aso_decisions`
- `aso_technicians`

---

## Development Workflow

### When Adding Feature to Flutter App:

```
Step 1: Design Feature
├─ Define user story
├─ Design UI/UX for mobile
├─ Define API requirements
└─ Plan database changes

Step 2: Implement Backend (FastAPI)
├─ Add/modify database models (if needed)
├─ Create Alembic migration (if needed)
├─ Add API endpoints
├─ Add WebSocket broadcasting
└─ Write tests

Step 3: Implement Flutter App
├─ Create models
├─ Add API service methods
├─ Build UI screens
├─ Implement offline support
└─ Test on device

Step 4: Implement React Admin Module ← MUST DO
├─ Add feature to corresponding module page
├─ Add WebSocket listener for real-time updates
├─ Add admin-specific enhancements
│  ├─ Advanced filters
│  ├─ Bulk operations
│  ├─ Export functionality
│  └─ Analytics/reporting
├─ Update dashboard/summary
└─ Write tests

Step 5: Update Documentation
├─ Update FEATURE_PARITY_TRACKER.md
├─ Update integration guide
└─ Update API documentation

Step 6: Test Integration
├─ Create record in Flutter app
├─ Verify appears in React Admin (real-time)
├─ Test CRUD operations from both sides
└─ Test with multiple concurrent users
```

---

## Feature Parity Checklist Template

Use this checklist when adding any feature:

```markdown
## Feature: [Feature Name]

### Planning
- [ ] User story defined
- [ ] Mobile UI designed
- [ ] Web admin UI designed
- [ ] API endpoints identified
- [ ] Database changes identified

### Backend Implementation
- [ ] Database models created/updated
- [ ] Migration created and tested
- [ ] API endpoints implemented
- [ ] WebSocket broadcasting added
- [ ] Tests written

### Flutter App Implementation
- [ ] Models created
- [ ] API service methods added
- [ ] UI screens implemented
- [ ] Offline support added (if applicable)
- [ ] Tested on iOS
- [ ] Tested on Android

### React Admin Module Implementation ← CRITICAL
- [ ] Feature added to module page
- [ ] WebSocket listener added
- [ ] Real-time updates working
- [ ] Admin-specific features added:
  - [ ] Advanced filtering
  - [ ] Bulk operations
  - [ ] Export functionality
  - [ ] Analytics/reporting
- [ ] Dashboard updated
- [ ] Tests written

### Integration Testing
- [ ] Create from Flutter → Appears in React Admin
- [ ] Update from Flutter → Updates in React Admin
- [ ] Create from React Admin → Appears in Flutter
- [ ] Real-time sync working
- [ ] Multiple concurrent users tested

### Documentation
- [ ] Feature tracker updated
- [ ] Integration guide updated
- [ ] API docs updated
- [ ] User documentation created
```

---

## Real-Time Sync Pattern

Every feature must follow this pattern:

### 1. Backend Endpoint with Broadcasting

```python
# app/routers/sales.py

@router.post("/orders", response_model=Order)
async def create_order(
    order: OrderCreate,
    source_app: str = Header(None, alias="X-Source-App"),  # Track which app
    db: Session = Depends(get_db)
):
    """Create order - can be called from any sales app"""
    service = SalesService(db)
    new_order = service.create_order(order)

    # Broadcast to React Admin Sales Module
    await sales_ws_manager.broadcast_order_created({
        "id": new_order.id,
        "order_number": new_order.order_number,
        "customer_name": new_order.customer_name,
        "total": float(new_order.total),
        "source_app": source_app or "unknown",  # field_sales|partner|retailer|consumer
        "created_by": new_order.created_by,
        "created_at": new_order.created_at.isoformat()
    })

    return new_order
```

### 2. Flutter App API Call

```dart
// lib/services/api_service.dart

Future<Order> createOrder(Order order) async {
  final token = await _getToken();

  final response = await http.post(
    Uri.parse('$baseUrl/api/sales/orders'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
      'X-Source-App': 'field_sales',  // Identify source
    },
    body: jsonEncode(order.toJson()),
  );

  if (response.statusCode == 200) {
    return Order.fromJson(jsonDecode(response.body));
  } else {
    throw Exception('Failed to create order');
  }
}
```

### 3. React Admin WebSocket Listener

```typescript
// frontend/src/hooks/useSalesWebSocket.ts

export const useSalesWebSocket = ({
  onOrderCreated,
  onOrderUpdated,
  // ... other callbacks
}: UseSalesWebSocketProps) => {
  const connect = useCallback(() => {
    const ws = new WebSocket(`ws://localhost:8000/api/sales/ws`)

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)

      switch (message.event) {
        case 'order_created':
          onOrderCreated?.(message.data)
          toast.success(
            `New order from ${message.data.source_app}: ${message.data.order_number}`
          )
          break
        // ... other cases
      }
    }
  }, [])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [])
}
```

### 4. React Module Page Integration

```typescript
// frontend/src/pages/sales/OrdersPage.tsx

const OrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([])

  // Real-time updates from ALL sales apps
  useSalesWebSocket({
    onOrderCreated: (newOrder) => {
      // Add to list with source app badge
      setOrders(prev => [newOrder, ...prev])
    },
    onOrderUpdated: (updatedOrder) => {
      setOrders(prev => prev.map(o =>
        o.id === updatedOrder.id ? updatedOrder : o
      ))
    }
  })

  return (
    <div>
      <h1>All Orders - من جميع التطبيقات</h1>
      {/* Show orders from all apps with source badges */}
      {orders.map(order => (
        <OrderCard
          key={order.id}
          order={order}
          sourceApp={order.source_app}  // Show which app created it
        />
      ))}
    </div>
  )
}
```

---

## Example: Adding "Client Visit Report" Feature

Let's walk through complete example:

### 1. Feature Requirements
```
Feature: Client Visit Report
- Sales rep visits client
- Records visit details (purpose, outcome, next steps)
- Attaches photos
- Creates follow-up tasks
```

### 2. Backend Implementation

```python
# app/models/sales.py
class ClientVisit(Base):
    __tablename__ = "sales_client_visits"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("sales_clients.id"))
    sales_rep_id = Column(Integer, ForeignKey("users.id"))
    visit_date = Column(DateTime)
    purpose = Column(String)
    outcome = Column(Text)
    next_steps = Column(Text)
    photos = Column(JSON)  # List of photo URLs
    created_at = Column(DateTime, default=datetime.utcnow)

# app/routers/sales.py
@router.post("/client-visits", response_model=ClientVisit)
async def create_client_visit(
    visit: ClientVisitCreate,
    db: Session = Depends(get_db)
):
    service = SalesService(db)
    new_visit = service.create_client_visit(visit)

    # Broadcast to React Admin
    await sales_ws_manager.broadcast_visit_created({
        "id": new_visit.id,
        "client_name": new_visit.client.name,
        "sales_rep_name": new_visit.sales_rep.full_name,
        "visit_date": new_visit.visit_date.isoformat(),
        "purpose": new_visit.purpose
    })

    return new_visit
```

### 3. Flutter Field Sales App

```dart
// lib/screens/create_visit_screen.dart
class CreateVisitScreen extends StatefulWidget {
  final Client client;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('تقرير زيارة عميل')),
      body: Form(
        child: Column(
          children: [
            TextFormField(
              controller: _purposeController,
              decoration: InputDecoration(labelText: 'Purpose - الغرض'),
            ),
            TextFormField(
              controller: _outcomeController,
              decoration: InputDecoration(labelText: 'Outcome - النتيجة'),
              maxLines: 3,
            ),
            TextFormField(
              controller: _nextStepsController,
              decoration: InputDecoration(labelText: 'Next Steps - الخطوات التالية'),
              maxLines: 3,
            ),
            // Photo upload buttons
            _buildPhotoSection(),
            ElevatedButton(
              onPressed: _submitVisit,
              child: Text('Submit Visit Report'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _submitVisit() async {
    final visit = ClientVisit(
      clientId: widget.client.id,
      visitDate: DateTime.now(),
      purpose: _purposeController.text,
      outcome: _outcomeController.text,
      nextSteps: _nextStepsController.text,
      photos: _uploadedPhotoUrls,
    );

    await _apiService.createClientVisit(visit);
    // Show success message and navigate back
  }
}
```

### 4. React Admin Sales Module

```typescript
// frontend/src/pages/sales/ClientVisitsPage.tsx

const ClientVisitsPage: React.FC = () => {
  const [visits, setVisits] = useState<ClientVisit[]>([])

  // Real-time updates
  useSalesWebSocket({
    onVisitCreated: (newVisit) => {
      setVisits(prev => [newVisit, ...prev])
      toast.success(`New visit by ${newVisit.sales_rep_name}`)
    }
  })

  useEffect(() => {
    fetchVisits()
  }, [])

  return (
    <div>
      <h1>Client Visits - زيارات العملاء</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard
          title="Total Visits Today"
          value={visitsToday}
        />
        <StatCard
          title="Active Sales Reps"
          value={activeSalesReps}
        />
        <StatCard
          title="Follow-ups Required"
          value={followUpsCount}
        />
      </div>

      {/* Visits Timeline */}
      <VisitsTimeline visits={visits} />

      {/* Filters & Analytics */}
      <VisitsAnalytics data={visits} />
    </div>
  )
}
```

---

## Summary

**Core Principle**:
> Every feature in any Flutter app MUST exist in its corresponding React Admin module, with the React Admin providing additional oversight, analytics, and administrative capabilities.

**Why This Matters**:
1. **Owner Control**: Owner sees EVERYTHING from all apps in one place
2. **Consistency**: Users get same features across web and mobile
3. **Real-Time Sync**: Changes appear instantly everywhere
4. **Better Analytics**: React Admin aggregates data from all apps
5. **Centralized Management**: One place to configure everything

**When Adding Feature**:
✅ Implement in Flutter app for field use
✅ Implement in React Admin module for oversight
✅ Add WebSocket broadcasting for real-time sync
✅ Test both directions
✅ Update documentation

This ensures your TSH ERP ecosystem remains synchronized and provides comprehensive control to management while empowering field staff with mobile tools.
