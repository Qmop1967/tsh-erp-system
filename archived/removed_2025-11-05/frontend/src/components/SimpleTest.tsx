import React from 'react'
import { useAuthStore } from '@/stores/authStore'

export const SimpleTest: React.FC = () => {
  const { user } = useAuthStore()

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      left: '10px', 
      background: 'red', 
      color: 'white', 
      padding: '10px', 
      zIndex: 9999 
    }}>
      <div>User: {user?.name || 'No user'}</div>
      <div>Admin: {user?.permissions?.includes('admin') ? 'YES' : 'NO'}</div>
      <div>Items: {user?.permissions?.includes('items.view') ? 'YES' : 'NO'}</div>
      <div>Permissions: {user?.permissions?.length || 0}</div>
    </div>
  )
}
