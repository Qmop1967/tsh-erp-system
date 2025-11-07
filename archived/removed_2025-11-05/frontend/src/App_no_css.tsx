function App() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      padding: '2rem', 
      backgroundColor: '#f8f9fa',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ 
        fontSize: '2rem', 
        fontWeight: 'bold', 
        color: '#333',
        marginBottom: '1rem'
      }}>
        🔍 TSH ERP System - Raw HTML Test
      </h1>
      <p style={{ color: '#666', marginBottom: '2rem' }}>
        Testing without any external CSS or frameworks...
      </p>
      
      <div style={{
        backgroundColor: 'white',
        padding: '1.5rem',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        border: '1px solid #ddd'
      }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#22c55e' }}>
          ✅ Success!
        </h2>
        <p style={{ color: '#666', marginTop: '0.5rem' }}>
          React app is rendering correctly with inline styles.
        </p>
        <div style={{ marginTop: '1rem' }}>
          <p style={{ fontSize: '0.875rem', color: '#666' }}>
            This confirms React is working. The issue is likely:
          </p>
          <ul style={{ marginTop: '1rem', paddingLeft: '1.5rem' }}>
            <li style={{ color: '#666', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
              • Tailwind CSS configuration
            </li>
            <li style={{ color: '#666', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
              • Component dependencies
            </li>
            <li style={{ color: '#666', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
              • Store initialization
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default App
