import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { CheckCircle, AlertTriangle, XCircle, Info, X } from 'lucide-react';

interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast = { ...toast, id };
    
    setToasts(prev => [...prev, newToast]);

    // Auto remove after duration
    const duration = toast.duration || 5000;
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, duration);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
}

function ToastContainer({ toasts, removeToast }: { toasts: Toast[]; removeToast: (id: string) => void }) {
  if (toasts.length === 0) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        maxWidth: '400px',
      }}
    >
      {toasts.map(toast => (
        <ToastItem key={toast.id} toast={toast} onRemove={() => removeToast(toast.id)} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: () => void }) {
  const getIcon = () => {
    switch (toast.type) {
      case 'success': return <CheckCircle size={20} />;
      case 'error': return <XCircle size={20} />;
      case 'warning': return <AlertTriangle size={20} />;
      case 'info': return <Info size={20} />;
    }
  };

  const getColors = () => {
    switch (toast.type) {
      case 'success': return { bg: '#f0fdf4', border: '#bbf7d0', text: '#15803d', icon: '#10b981' };
      case 'error': return { bg: '#fef2f2', border: '#fecaca', text: '#dc2626', icon: '#ef4444' };
      case 'warning': return { bg: '#fffbeb', border: '#fde68a', text: '#d97706', icon: '#f59e0b' };
      case 'info': return { bg: '#eff6ff', border: '#bfdbfe', text: '#2563eb', icon: '#3b82f6' };
    }
  };

  const colors = getColors();

  return (
    <div
      style={{
        backgroundColor: colors.bg,
        border: `1px solid ${colors.border}`,
        borderRadius: '8px',
        padding: '12px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        animation: 'slideInRight 0.3s ease-out',
      }}
    >
      <div style={{ color: colors.icon, flexShrink: 0 }}>
        {getIcon()}
      </div>
      <div style={{ flex: 1 }}>
        <p style={{ 
          margin: 0, 
          fontSize: '14px', 
          fontWeight: '500', 
          color: colors.text,
          lineHeight: '1.4'
        }}>
          {toast.message}
        </p>
      </div>
      <button
        onClick={onRemove}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: '4px',
          borderRadius: '4px',
          color: colors.text,
          opacity: 0.7,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
        onMouseOver={(e) => e.currentTarget.style.opacity = '1'}
        onMouseOut={(e) => e.currentTarget.style.opacity = '0.7'}
      >
        <X size={16} />
      </button>
    </div>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

// Convenience hooks
export function useSuccessToast() {
  const { addToast } = useToast();
  return (message: string, duration?: number) => addToast({ message, type: 'success', duration });
}

export function useErrorToast() {
  const { addToast } = useToast();
  return (message: string, duration?: number) => addToast({ message, type: 'error', duration });
}

export function useWarningToast() {
  const { addToast } = useToast();
  return (message: string, duration?: number) => addToast({ message, type: 'warning', duration });
}

export function useInfoToast() {
  const { addToast } = useToast();
  return (message: string, duration?: number) => addToast({ message, type: 'info', duration });
}