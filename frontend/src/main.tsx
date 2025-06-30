import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import { LanguageInitializer } from './components/LanguageInitializer'
import './index.css'

console.log('🚀 Starting TSH ERP System...')

const root = document.getElementById('root')!
console.log('Root element:', root)

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <BrowserRouter>
      <LanguageInitializer>
        <App />
      </LanguageInitializer>
    </BrowserRouter>
  </React.StrictMode>,
)
