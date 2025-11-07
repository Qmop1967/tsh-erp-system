// IMPORTANT: Initialize error suppression FIRST before any other imports
// This must be the very first code that runs
import { initErrorSuppression } from './utils/errorSuppression'
initErrorSuppression();

import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { NotificationProvider } from './components/ui/NotificationProvider'
import App from './App.tsx'
import './index.css'

console.log('🚀 Starting TSH ERP System - Full Tailwind Mode...');

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

const root = document.getElementById('root')!
console.log('Root element:', root)

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <NotificationProvider>
          <App />
        </NotificationProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
