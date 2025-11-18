console.log('Starting React app...')

import { createRoot } from 'react-dom/client'

function App() {
  console.log('App component rendering...')
  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0', minHeight: '100vh' }}>
      <h1>🔍 Minimal React Test</h1>
      <p>If you see this, React is working!</p>
      <div style={{ 
        backgroundColor: 'white', 
        padding: '20px', 
        borderRadius: '8px',
        marginTop: '20px' 
      }}>
        <h2 style={{ color: 'green' }}>✅ React Loaded Successfully</h2>
        <p>Current time: {new Date().toLocaleTimeString()}</p>
      </div>
    </div>
  )
}

console.log('Creating root...')
const container = document.getElementById('root')
if (container) {
  console.log('Root element found, rendering app...')
  const root = createRoot(container)
  root.render(<App />)
} else {
  console.error('Root element not found!')
}
