export function SimpleDashboard() {
  console.log('🎯 SimpleDashboard component rendering...')
  
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#1f2937', marginBottom: '20px' }}>
        TSH ERP System - Working Dashboard
      </h1>
      
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '20px' }}>
        <h2 style={{ color: '#059669', marginBottom: '15px' }}>💰 Financial Overview</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
          <div style={{ backgroundColor: '#ecfdf5', padding: '15px', borderRadius: '6px', border: '1px solid #d1fae5' }}>
            <h3 style={{ color: '#065f46', fontSize: '14px', margin: '0 0 8px 0' }}>Total Receivables</h3>
            <p style={{ color: '#047857', fontSize: '24px', fontWeight: 'bold', margin: '0' }}>$125,430.50</p>
            <p style={{ color: '#059669', fontSize: '12px', margin: '5px 0 0 0' }}>Amount owed to us</p>
          </div>
          
          <div style={{ backgroundColor: '#fef2f2', padding: '15px', borderRadius: '6px', border: '1px solid #fecaca' }}>
            <h3 style={{ color: '#7f1d1d', fontSize: '14px', margin: '0 0 8px 0' }}>Total Payables</h3>
            <p style={{ color: '#dc2626', fontSize: '24px', fontWeight: 'bold', margin: '0' }}>$89,720.25</p>
            <p style={{ color: '#ef4444', fontSize: '12px', margin: '5px 0 0 0' }}>Amount we owe</p>
          </div>
          
          <div style={{ backgroundColor: '#eff6ff', padding: '15px', borderRadius: '6px', border: '1px solid #bfdbfe' }}>
            <h3 style={{ color: '#1e3a8a', fontSize: '14px', margin: '0 0 8px 0' }}>Stock Value</h3>
            <p style={{ color: '#2563eb', fontSize: '24px', fontWeight: 'bold', margin: '0' }}>$234,890.75</p>
            <p style={{ color: '#3b82f6', fontSize: '12px', margin: '5px 0 0 0' }}>Current inventory cost</p>
          </div>
        </div>
      </div>

      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '20px' }}>
        <h2 style={{ color: '#7c3aed', marginBottom: '15px' }}>📦 Inventory Summary</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          <div style={{ backgroundColor: '#faf5ff', padding: '15px', borderRadius: '6px', border: '1px solid #e9d5ff' }}>
            <h3 style={{ color: '#581c87', fontSize: '14px', margin: '0 0 8px 0' }}>Positive Items</h3>
            <p style={{ color: '#7c3aed', fontSize: '24px', fontWeight: 'bold', margin: '0' }}>1,247</p>
            <p style={{ color: '#8b5cf6', fontSize: '12px', margin: '5px 0 0 0' }}>Items in warehouse</p>
          </div>
          
          <div style={{ backgroundColor: '#f0f9ff', padding: '15px', borderRadius: '6px', border: '1px solid #bae6fd' }}>
            <h3 style={{ color: '#1e40af', fontSize: '14px', margin: '0 0 8px 0' }}>Total Pieces</h3>
            <p style={{ color: '#3730a3', fontSize: '24px', fontWeight: 'bold', margin: '0' }}>15,892</p>
            <p style={{ color: '#4f46e5', fontSize: '12px', margin: '5px 0 0 0' }}>Pieces available</p>
          </div>
        </div>
      </div>

      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '20px' }}>
        <h2 style={{ color: '#ea580c', marginBottom: '15px' }}>👥 Staff Summary</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          <div style={{ backgroundColor: '#fff7ed', padding: '15px', borderRadius: '6px', border: '1px solid #fed7aa' }}>
            <h3 style={{ color: '#9a3412', fontSize: '14px', margin: '0 0 8px 0' }}>Partner Salesmen</h3>
            <p style={{ color: '#ea580c', fontSize: '24px', fontWeight: 'bold', margin: '0' }}>12</p>
          </div>
          
          <div style={{ backgroundColor: '#fefce8', padding: '15px', borderRadius: '6px', border: '1px solid #fde047' }}>
            <h3 style={{ color: '#a16207', fontSize: '14px', margin: '0 0 8px 0' }}>Travel Salespersons</h3>
            <p style={{ color: '#ca8a04', fontSize: '24px', fontWeight: 'bold', margin: '0' }}>8</p>
          </div>
        </div>
      </div>

      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '20px' }}>
        <h2 style={{ color: '#059669', marginBottom: '15px' }}>💵 Money Boxes</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px', marginBottom: '15px' }}>
          <div style={{ backgroundColor: '#ecfdf5', padding: '12px', borderRadius: '6px', border: '1px solid #d1fae5' }}>
            <h4 style={{ color: '#065f46', fontSize: '12px', margin: '0 0 5px 0' }}>Main Box</h4>
            <p style={{ color: '#047857', fontSize: '18px', fontWeight: 'bold', margin: '0' }}>$45,230.50</p>
          </div>
          <div style={{ backgroundColor: '#ecfdf5', padding: '12px', borderRadius: '6px', border: '1px solid #d1fae5' }}>
            <h4 style={{ color: '#065f46', fontSize: '12px', margin: '0 0 5px 0' }}>Frat Awsat</h4>
            <p style={{ color: '#047857', fontSize: '18px', fontWeight: 'bold', margin: '0' }}>$12,840.25</p>
          </div>
          <div style={{ backgroundColor: '#ecfdf5', padding: '12px', borderRadius: '6px', border: '1px solid #d1fae5' }}>
            <h4 style={{ color: '#065f46', fontSize: '12px', margin: '0 0 5px 0' }}>South Vector</h4>
            <p style={{ color: '#047857', fontSize: '18px', fontWeight: 'bold', margin: '0' }}>$8,920.75</p>
          </div>
          <div style={{ backgroundColor: '#ecfdf5', padding: '12px', borderRadius: '6px', border: '1px solid #d1fae5' }}>
            <h4 style={{ color: '#065f46', fontSize: '12px', margin: '0 0 5px 0' }}>North Vector</h4>
            <p style={{ color: '#047857', fontSize: '18px', fontWeight: 'bold', margin: '0' }}>$15,670.00</p>
          </div>
          <div style={{ backgroundColor: '#ecfdf5', padding: '12px', borderRadius: '6px', border: '1px solid #d1fae5' }}>
            <h4 style={{ color: '#065f46', fontSize: '12px', margin: '0 0 5px 0' }}>West Vector</h4>
            <p style={{ color: '#047857', fontSize: '18px', fontWeight: 'bold', margin: '0' }}>$9,450.50</p>
          </div>
          <div style={{ backgroundColor: '#ecfdf5', padding: '12px', borderRadius: '6px', border: '1px solid #d1fae5' }}>
            <h4 style={{ color: '#065f46', fontSize: '12px', margin: '0 0 5px 0' }}>Dayla Box</h4>
            <p style={{ color: '#047857', fontSize: '18px', fontWeight: 'bold', margin: '0' }}>$6,780.25</p>
          </div>
          <div style={{ backgroundColor: '#ecfdf5', padding: '12px', borderRadius: '6px', border: '1px solid #d1fae5' }}>
            <h4 style={{ color: '#065f46', fontSize: '12px', margin: '0 0 5px 0' }}>Baghdad Box</h4>
            <p style={{ color: '#047857', fontSize: '18px', fontWeight: 'bold', margin: '0' }}>$22,140.75</p>
          </div>
        </div>
        <div style={{ backgroundColor: '#d1fae5', padding: '15px', borderRadius: '6px', border: '2px solid #059669' }}>
          <h3 style={{ color: '#065f46', fontSize: '16px', margin: '0 0 8px 0' }}>Total Cash</h3>
          <p style={{ color: '#047857', fontSize: '32px', fontWeight: 'bold', margin: '0' }}>$121,032.00</p>
        </div>
      </div>

      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h2 style={{ color: '#2563eb', marginBottom: '15px' }}>⚡ Quick Navigation</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
          <a href="/users" style={{ backgroundColor: '#eff6ff', padding: '15px', borderRadius: '6px', border: '1px solid #bfdbfe', textDecoration: 'none', textAlign: 'center', color: '#1d4ed8' }}>
            <div>👥</div>
            <div style={{ marginTop: '5px', fontSize: '14px', fontWeight: '500' }}>Users</div>
          </a>
          <a href="/hr/users" style={{ backgroundColor: '#eff6ff', padding: '15px', borderRadius: '6px', border: '1px solid #bfdbfe', textDecoration: 'none', textAlign: 'center', color: '#1d4ed8' }}>
            <div>🏢</div>
            <div style={{ marginTop: '5px', fontSize: '14px', fontWeight: '500' }}>HR</div>
          </a>
          <a href="/sales/customers" style={{ backgroundColor: '#eff6ff', padding: '15px', borderRadius: '6px', border: '1px solid #bfdbfe', textDecoration: 'none', textAlign: 'center', color: '#1d4ed8' }}>
            <div>🛒</div>
            <div style={{ marginTop: '5px', fontSize: '14px', fontWeight: '500' }}>Sales</div>
          </a>
          <a href="/inventory/items" style={{ backgroundColor: '#eff6ff', padding: '15px', borderRadius: '6px', border: '1px solid #bfdbfe', textDecoration: 'none', textAlign: 'center', color: '#1d4ed8' }}>
            <div>📦</div>
            <div style={{ marginTop: '5px', fontSize: '14px', fontWeight: '500' }}>Inventory</div>
          </a>
          <a href="/accounting/chart-of-accounts" style={{ backgroundColor: '#eff6ff', padding: '15px', borderRadius: '6px', border: '1px solid #bfdbfe', textDecoration: 'none', textAlign: 'center', color: '#1d4ed8' }}>
            <div>🧮</div>
            <div style={{ marginTop: '5px', fontSize: '14px', fontWeight: '500' }}>Accounting</div>
          </a>
          <a href="/pos" style={{ backgroundColor: '#eff6ff', padding: '15px', borderRadius: '6px', border: '1px solid #bfdbfe', textDecoration: 'none', textAlign: 'center', color: '#1d4ed8' }}>
            <div>💳</div>
            <div style={{ marginTop: '5px', fontSize: '14px', fontWeight: '500' }}>POS</div>
          </a>
          <a href="/financial/dashboard" style={{ backgroundColor: '#eff6ff', padding: '15px', borderRadius: '6px', border: '1px solid #bfdbfe', textDecoration: 'none', textAlign: 'center', color: '#1d4ed8' }}>
            <div>💰</div>
            <div style={{ marginTop: '5px', fontSize: '14px', fontWeight: '500' }}>Financial</div>
          </a>
          <a href="/settings" style={{ backgroundColor: '#eff6ff', padding: '15px', borderRadius: '6px', border: '1px solid #bfdbfe', textDecoration: 'none', textAlign: 'center', color: '#1d4ed8' }}>
            <div>⚙️</div>
            <div style={{ marginTop: '5px', fontSize: '14px', fontWeight: '500' }}>Settings</div>
          </a>
        </div>
      </div>
      
      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f3f4f6', borderRadius: '6px', textAlign: 'center' }}>
        <p style={{ color: '#6b7280', fontSize: '14px', margin: '0' }}>
          TSH ERP System - Demo Mode | All data is simulated for demonstration
        </p>
      </div>
    </div>
  )
}
