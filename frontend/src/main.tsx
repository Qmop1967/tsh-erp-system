import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import './minimal.css'

console.log('🚀 Starting TSH ERP System - Minimal Mode...')

const root = document.getElementById('root')!
console.log('Root element:', root)

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
