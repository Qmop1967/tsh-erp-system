# TSH ERP Feature Parity Tracker

Track features across React Admin modules and their corresponding Flutter apps to ensure synchronization.

**Legend:**
- ✅ Implemented and synced
- 🚧 In progress
- ❌ Not implemented
- ⚠️ Partial (exists but not synced)

---

## 📊 ACCOUNTING MODULE

### Module: React Admin - Accounting
### Apps: TSH Accounting Flutter App

| Feature | React Admin | Flutter App | Real-Time Sync | Notes |
|---------|-------------|-------------|----------------|-------|
| **Dashboard** |
| View total assets/liabilities/equity | ✅ | ✅ | ✅ | Working |
| Net profit/loss | ⚠️ | ⚠️ | ❌ | Using fallback data |
| Cash flow summary | ⚠️ | ⚠️ | ❌ | Using fallback data |
| **Chart of Accounts** |
| View chart of accounts | ✅ | ⚠️ | ❌ | Flutter placeholder |
| Create accounts | ✅ | ❌ | N/A | Admin only |
| Edit accounts | ✅ | ❌ | N/A | Admin only |
| Account hierarchy | ✅ | ⚠️ | ❌ | Flutter placeholder |
| **Journal Entries** |
| View journal entries | ✅ | ✅ | ✅ | Working |
| Create journal entries | ✅ | 🚧 | ✅ | Flutter form pending |
| Edit journal entries | ✅ | ❌ | ❌ | Not yet implemented |
| Post journal entries | ✅ | ❌ | ❌ | Admin only |
| Reverse journal entries | ✅ | ❌ | N/A | Admin only |
| **Financial Reports** |
| Balance sheet | ✅ | ❌ | N/A | Admin only |
| Income statement | ✅ | ❌ | N/A | Admin only |
| Trial balance | ✅ | ❌ | N/A | Admin only |
| Cash flow statement | ✅ | ❌ | N/A | Admin only |
| **Period Management** |
| View fiscal years | ✅ | ❌ | N/A | Admin only |
| Create fiscal years | ✅ | ❌ | N/A | Admin only |
| Close periods | ✅ | ❌ | N/A | Admin only |

**Priority Tasks:**
1. 🚧 Complete journal entry creation form in Flutter app
2. ❌ Implement journal entry editing in both apps
3. ❌ Complete chart of accounts screen in Flutter app
4. ⚠️ Fix backend summary endpoint to return real data

---

## 💰 SALES MODULE

### Module: React Admin - Sales
### Apps: Field Sales Rep, Partner Network, Retailer, Consumer, Client Management

| Feature | React Admin | Field Sales | Partner App | Retailer App | Consumer App | Real-Time Sync | Notes |
|---------|-------------|-------------|-------------|--------------|--------------|----------------|-------|
| **Dashboard** |
| Total sales overview | ⚠️ | ❌ | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Sales by channel | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Not yet built |
| Top products | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Not yet built |
| **Clients Management** |
| View all clients | ⚠️ | ❌ | ❌ | N/A | N/A | ❌ | Basic exists |
| Create client | ❌ | ❌ | ❌ | N/A | N/A | ❌ | Needs implementation |
| Edit client | ❌ | ❌ | ❌ | N/A | N/A | ❌ | Needs implementation |
| Client categories | ❌ | ❌ | ❌ | N/A | N/A | ❌ | Needs implementation |
| Credit limits | ❌ | ❌ | ❌ | N/A | N/A | ❌ | Needs implementation |
| **Orders Management** |
| View all orders | ⚠️ | ❌ | ❌ | ❌ | ❌ | ❌ | Basic exists |
| Create order | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Edit order | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Track order status | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Order by channel filter | ❌ | N/A | N/A | N/A | N/A | ❌ | Admin feature |
| **Products** |
| Product catalog | ⚠️ | ❌ | ❌ | ❌ | ❌ | ❌ | Basic exists |
| Product details | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Pricing management | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Admin only |
| Inventory levels | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Needs integration |
| **Partners & Retailers** |
| Partner management | ❌ | N/A | ❌ | N/A | N/A | ❌ | Needs implementation |
| Retailer management | ❌ | ❌ | ❌ | ❌ | N/A | ❌ | Needs implementation |
| Commission tracking | ❌ | N/A | ❌ | N/A | N/A | ❌ | Needs implementation |
| **Sales Team** |
| Sales rep performance | ❌ | ❌ | N/A | N/A | N/A | ❌ | Needs implementation |
| Territory management | ❌ | ❌ | N/A | N/A | N/A | ❌ | Needs implementation |
| Target setting | ❌ | ❌ | N/A | N/A | N/A | ❌ | Admin only |
| **Client Visits** |
| View all visits | ❌ | ❌ | N/A | N/A | N/A | ❌ | Needs implementation |
| Create visit report | ❌ | ❌ | N/A | N/A | N/A | ❌ | Needs implementation |
| Visit analytics | ❌ | N/A | N/A | N/A | N/A | ❌ | Admin only |

**Priority Tasks:**
1. ❌ Build Field Sales Rep Flutter app
2. ❌ Build Partner Network Flutter app
3. ❌ Build Retailer Flutter app
4. ❌ Build Consumer Flutter app
5. ❌ Implement complete sales module in React Admin
6. ❌ Set up WebSocket broadcasting for sales events

---

## 📦 INVENTORY MODULE

### Module: React Admin - Inventory
### Apps: Warehouse Management App, Stock Management App

| Feature | React Admin | Warehouse App | Stock Mgmt App | Real-Time Sync | Notes |
|---------|-------------|---------------|----------------|----------------|-------|
| **Dashboard** |
| Total stock value | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Low stock alerts | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Stock by warehouse | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| **Products** |
| Product master data | ⚠️ | ❌ | ❌ | ❌ | Basic exists |
| SKU management | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Product variants | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| **Warehouses** |
| Warehouse list | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Location tracking | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Bin management | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| **Stock Movements** |
| View movements | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Stock transfers | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Stock adjustments | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Cycle counting | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| **Receiving** |
| Receive goods | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| GRN creation | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Quality check | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| **Picking & Packing** |
| Pick orders | ❌ | ❌ | N/A | ❌ | Needs implementation |
| Pack orders | ❌ | ❌ | N/A | ❌ | Needs implementation |
| Barcode scanning | ❌ | ❌ | ❌ | ❌ | Needs implementation |

**Priority Tasks:**
1. ❌ Build Warehouse Management Flutter app
2. ❌ Build Stock Management Flutter app
3. ❌ Implement inventory module in React Admin
4. ❌ Set up WebSocket broadcasting for inventory events

---

## 🔧 AFTER-SALES OPERATIONS MODULE

### Module: React Admin - After-Sales Operations
### Apps: Technician Service App

| Feature | React Admin | Technician App | Real-Time Sync | Notes |
|---------|-------------|----------------|----------------|-------|
| **Dashboard** |
| Pending requests | ✅ | ✅ | ✅ | Working |
| Jobs in progress | ✅ | ✅ | ✅ | Working |
| Completed today | ✅ | ✅ | ✅ | Working |
| **Service Requests** |
| View all requests | ✅ | ✅ | ✅ | Working |
| Create request | ✅ | ✅ | ✅ | Working |
| Assign to technician | ✅ | ❌ | N/A | Admin only |
| Status tracking | ✅ | ✅ | ✅ | Working |
| **Maintenance Jobs** |
| View jobs | ✅ | ✅ | ✅ | Working |
| Job check-in/out | ❌ | ✅ | ✅ | Working |
| Update job status | ✅ | ✅ | ✅ | Working |
| Parts used tracking | ✅ | ✅ | ✅ | Working |
| Photo documentation | ❌ | ✅ | ✅ | Working |
| Customer signature | ❌ | ✅ | ✅ | Working |
| **Returns** |
| View return requests | ✅ | ✅ | ✅ | Working |
| Inspection | ✅ | ✅ | ✅ | Working |
| Decision tracking | ✅ | ❌ | N/A | Admin only |
| **Warranty** |
| Warranty registration | ✅ | ❌ | ❌ | Needs implementation |
| Claims processing | ✅ | ❌ | ❌ | Needs implementation |
| **Technician Management** |
| Technician scheduling | ✅ | N/A | N/A | Admin only |
| Performance tracking | ✅ | ✅ | ✅ | Working |
| Skills management | ✅ | ❌ | N/A | Admin only |

**Priority Tasks:**
1. ⚠️ Add warranty features to both apps
2. ✅ ASO module mostly complete

---

## 👥 HR MODULE

### Module: React Admin - HR
### Apps: Employee Self-Service App, Time Tracking App

| Feature | React Admin | Employee App | Time Track App | Real-Time Sync | Notes |
|---------|-------------|--------------|----------------|----------------|-------|
| **Dashboard** |
| Employee count | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Attendance overview | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Leave requests | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| **Employee Management** |
| View employees | ❌ | ❌ | N/A | ❌ | Needs implementation |
| Create employee | ❌ | ❌ | N/A | ❌ | Admin only |
| Edit employee | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Employee documents | ❌ | ❌ | N/A | ❌ | Needs implementation |
| **Attendance** |
| View attendance | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Check-in/out | ❌ | ❌ | ❌ | ❌ | Needs implementation |
| Attendance reports | ❌ | N/A | N/A | ❌ | Admin only |
| **Leave Management** |
| View leave requests | ❌ | ❌ | N/A | ❌ | Needs implementation |
| Submit leave request | ❌ | ❌ | N/A | ❌ | Needs implementation |
| Approve/reject | ❌ | N/A | N/A | ❌ | Admin only |
| Leave balance | ❌ | ❌ | N/A | ❌ | Needs implementation |
| **Payroll** |
| View payroll | ❌ | ❌ | N/A | ❌ | Needs implementation |
| Payslips | ❌ | ❌ | N/A | ❌ | Needs implementation |
| Deductions | ❌ | N/A | N/A | ❌ | Admin only |

**Priority Tasks:**
1. ❌ Build Employee Self-Service Flutter app
2. ❌ Build Time Tracking Flutter app
3. ❌ Implement HR module in React Admin
4. ❌ Set up WebSocket broadcasting for HR events

---

## Development Priority Matrix

### High Priority (Next Sprint)
1. **Accounting**: Complete journal entry creation in Flutter app
2. **Accounting**: Implement edit journal entry in both apps
3. **Sales**: Start building Field Sales Rep Flutter app
4. **Sales**: Implement basic sales module features in React Admin

### Medium Priority
1. **Inventory**: Design and plan inventory module
2. **HR**: Design and plan HR module
3. **Sales**: Build Partner Network Flutter app
4. **Sales**: Build Retailer Flutter app

### Low Priority
1. **Sales**: Build Consumer Flutter app
2. **Advanced reporting** across all modules
3. **Mobile app optimization** for offline mode
4. **Performance optimization** for large datasets

---

## WebSocket Events Tracking

Track which real-time events are implemented for each module:

### Accounting Events
| Event | Backend Broadcast | React Listen | Flutter Listen | Status |
|-------|-------------------|--------------|----------------|--------|
| `journal_entry_created` | ✅ | ✅ | N/A | ✅ Working |
| `journal_entry_updated` | ✅ | ✅ | N/A | ✅ Working |
| `journal_entry_posted` | ✅ | ✅ | N/A | ✅ Working |
| `accounting_summary_updated` | ✅ | ✅ | N/A | ⚠️ Partial |

### Sales Events (To Be Implemented)
| Event | Backend Broadcast | React Listen | Flutter Apps Listen | Status |
|-------|-------------------|--------------|---------------------|--------|
| `order_created` | ❌ | ❌ | ❌ | ❌ Not implemented |
| `order_updated` | ❌ | ❌ | ❌ | ❌ Not implemented |
| `client_created` | ❌ | ❌ | ❌ | ❌ Not implemented |
| `visit_created` | ❌ | ❌ | ❌ | ❌ Not implemented |
| `sales_summary_updated` | ❌ | ❌ | ❌ | ❌ Not implemented |

### Inventory Events (To Be Implemented)
| Event | Backend Broadcast | React Listen | Flutter Apps Listen | Status |
|-------|-------------------|--------------|---------------------|--------|
| `stock_updated` | ❌ | ❌ | ❌ | ❌ Not implemented |
| `transfer_created` | ❌ | ❌ | ❌ | ❌ Not implemented |
| `goods_received` | ❌ | ❌ | ❌ | ❌ Not implemented |

### ASO Events
| Event | Backend Broadcast | React Listen | Flutter Listen | Status |
|-------|-------------------|--------------|----------------|--------|
| `service_request_created` | ✅ | ✅ | ✅ | ✅ Working |
| `job_updated` | ✅ | ✅ | ✅ | ✅ Working |
| `return_created` | ✅ | ✅ | ✅ | ✅ Working |

### HR Events (To Be Implemented)
| Event | Backend Broadcast | React Listen | Flutter Apps Listen | Status |
|-------|-------------------|--------------|---------------------|--------|
| `attendance_recorded` | ❌ | ❌ | ❌ | ❌ Not implemented |
| `leave_request_created` | ❌ | ❌ | ❌ | ❌ Not implemented |
| `leave_approved` | ❌ | ❌ | ❌ | ❌ Not implemented |

---

## Notes

**Last Updated**: 2025-01-24

**Key Insights**:
1. Accounting module is most complete with working real-time sync
2. ASO module has good coverage for technician app
3. Sales, Inventory, and HR modules need significant work
4. Priority should be completing accounting features first, then sales module

**Recommendations**:
1. Complete accounting module before starting new modules
2. Build one sales app at a time, starting with Field Sales Rep
3. Ensure each feature is implemented in both React and Flutter before moving to next
4. Set up WebSocket infrastructure for each module before building features
