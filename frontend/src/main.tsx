import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import App from './App.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'
import { ToastProvider } from './components/ui/toast'
import './minimal.css'

console.log('🚀 Starting TSH ERP System - Minimal Mode...')

// Create a QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

const root = document.getElementById('root')!
console.log('Root element:', root)

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </ToastProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)
