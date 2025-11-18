export function SimpleDashboardPage() {
  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '16px', color: '#111827' }}>
        Dashboard
      </h1>
      <p style={{ fontSize: '16px', color: '#6b7280', marginBottom: '32px' }}>
        Welcome back! Here's what's happening with your business today.
      </p>

      {/* Stats Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
        gap: '24px',
        marginBottom: '32px'
      }}>
        {/* Total Revenue */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '24px', 
          borderRadius: '12px', 
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
            Total Revenue
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>
            $1,500,000.00
          </div>
          <div style={{ fontSize: '12px', color: '#10b981' }}>
            +12.5% from last month
          </div>
        </div>

        {/* Total Employees */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '24px', 
          borderRadius: '12px', 
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
            Total Employees
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>
            156
          </div>
          <div style={{ fontSize: '12px', color: '#10b981' }}>
            +3 new this month
          </div>
        </div>

        {/* Inventory Items */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '24px', 
          borderRadius: '12px', 
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
            Inventory Items
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>
            1,247
          </div>
          <div style={{ fontSize: '12px', color: '#f59e0b' }}>
            23 low stock • 12 out of stock
          </div>
        </div>

        {/* Total Cash */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '24px', 
          borderRadius: '12px', 
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
            Total Cash
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>
            $121,033.00
          </div>
          <div style={{ fontSize: '12px', color: '#6b7280' }}>
            Across all money boxes
          </div>
        </div>
      </div>

      {/* Financial Overview */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px', color: '#111827' }}>
          💰 Financial Overview
        </h2>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
          gap: '24px'
        }}>
          <div style={{ 
            backgroundColor: '#dcfce7', 
            padding: '24px', 
            borderRadius: '12px',
            border: '1px solid #86efac'
          }}>
            <div style={{ fontSize: '14px', color: '#166534', marginBottom: '8px' }}>
              Total Receivables
            </div>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#166534' }}>
              $125,430.50
            </div>
            <div style={{ fontSize: '12px', color: '#166534', marginTop: '4px' }}>
              Amount owed to us
            </div>
          </div>

          <div style={{ 
            backgroundColor: '#fee2e2', 
            padding: '24px', 
            borderRadius: '12px',
            border: '1px solid #fca5a5'
          }}>
            <div style={{ fontSize: '14px', color: '#991b1b', marginBottom: '8px' }}>
              Total Payables
            </div>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#991b1b' }}>
              $89,720.25
            </div>
            <div style={{ fontSize: '12px', color: '#991b1b', marginTop: '4px' }}>
              Amount we owe
            </div>
          </div>

          <div style={{ 
            backgroundColor: '#dbeafe', 
            padding: '24px', 
            borderRadius: '12px',
            border: '1px solid #93c5fd'
          }}>
            <div style={{ fontSize: '14px', color: '#1e40af', marginBottom: '8px' }}>
              Stock Value
            </div>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#1e40af' }}>
              $234,890.75
            </div>
            <div style={{ fontSize: '12px', color: '#1e40af', marginTop: '4px' }}>
              1,247 items • 15,892 pieces
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px', color: '#111827' }}>
          ⚡ Quick Actions
        </h2>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button style={{ 
            padding: '12px 24px', 
            backgroundColor: '#3b82f6', 
            color: 'white', 
            border: 'none', 
            borderRadius: '8px', 
            fontSize: '14px', 
            fontWeight: '600',
            cursor: 'pointer'
          }}>
            + New Sale
          </button>
          <button style={{ 
            padding: '12px 24px', 
            backgroundColor: '#10b981', 
            color: 'white', 
            border: 'none', 
            borderRadius: '8px', 
            fontSize: '14px', 
            fontWeight: '600',
            cursor: 'pointer'
          }}>
            + Add Item
          </button>
          <button style={{ 
            padding: '12px 24px', 
            backgroundColor: '#f59e0b', 
            color: 'white', 
            border: 'none', 
            borderRadius: '8px', 
            fontSize: '14px', 
            fontWeight: '600',
            cursor: 'pointer'
          }}>
            + New Customer
          </button>
          <button style={{ 
            padding: '12px 24px', 
            backgroundColor: '#8b5cf6', 
            color: 'white', 
            border: 'none', 
            borderRadius: '8px', 
            fontSize: '14px', 
            fontWeight: '600',
            cursor: 'pointer'
          }}>
            View Reports
          </button>
        </div>
      </div>
    </div>
  );
}
