import { io, Socket } from 'socket.io-client';
import { AuthManager } from './api-client';
import type { SocketEvent } from '@/types/tds';

// Socket Configuration
const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'ws://localhost:8000';
const RECONNECTION_DELAY = 5000; // 5 seconds
const MAX_RECONNECTION_ATTEMPTS = 10;

// Socket Event Types
export type SocketEventType =
  | 'sync_completed'
  | 'alert_created'
  | 'queue_updated'
  | 'health_changed'
  | 'webhook_received'
  | 'circuit_breaker_state_changed';

// Socket Event Handlers
export type SocketEventHandler<T = any> = (data: T) => void;

class SocketManager {
  private socket: Socket | null = null;
  private eventHandlers: Map<SocketEventType, Set<SocketEventHandler>> = new Map();
  private reconnectionAttempts = 0;
  private isConnecting = false;

  constructor() {
    // Initialize event handler sets
    const eventTypes: SocketEventType[] = [
      'sync_completed',
      'alert_created',
      'queue_updated',
      'health_changed',
      'webhook_received',
      'circuit_breaker_state_changed',
    ];

    eventTypes.forEach(type => {
      this.eventHandlers.set(type, new Set());
    });
  }

  // Connect to Socket.IO server
  connect(): void {
    if (this.socket?.connected || this.isConnecting) {
      console.log('Socket already connected or connecting');
      return;
    }

    this.isConnecting = true;
    const token = AuthManager.getToken();

    if (!token) {
      console.error('No authentication token found. Cannot connect to socket.');
      this.isConnecting = false;
      return;
    }

    this.socket = io(SOCKET_URL, {
      auth: {
        token,
      },
      reconnection: true,
      reconnectionDelay: RECONNECTION_DELAY,
      reconnectionAttempts: MAX_RECONNECTION_ATTEMPTS,
      transports: ['websocket', 'polling'],
    });

    this.setupEventListeners();
    this.isConnecting = false;
  }

  // Disconnect from Socket.IO server
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // Setup built-in socket event listeners
  private setupEventListeners(): void {
    if (!this.socket) return;

    // Connection events
    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket?.id);
      this.reconnectionAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
      if (reason === 'io server disconnect') {
        // Server disconnected the socket, try to reconnect manually
        setTimeout(() => this.connect(), RECONNECTION_DELAY);
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
      this.reconnectionAttempts++;

      if (this.reconnectionAttempts >= MAX_RECONNECTION_ATTEMPTS) {
        console.error('Max reconnection attempts reached');
        this.disconnect();
      }
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('Socket reconnected after', attemptNumber, 'attempts');
      this.reconnectionAttempts = 0;
    });

    this.socket.on('reconnect_attempt', () => {
      console.log('Attempting to reconnect...');
    });

    this.socket.on('reconnect_error', (error) => {
      console.error('Socket reconnection error:', error);
    });

    this.socket.on('reconnect_failed', () => {
      console.error('Socket reconnection failed');
    });

    // TDS-specific events
    this.socket.on('sync_completed', (data) => {
      this.emitToHandlers('sync_completed', data);
    });

    this.socket.on('alert_created', (data) => {
      this.emitToHandlers('alert_created', data);
    });

    this.socket.on('queue_updated', (data) => {
      this.emitToHandlers('queue_updated', data);
    });

    this.socket.on('health_changed', (data) => {
      this.emitToHandlers('health_changed', data);
    });

    this.socket.on('webhook_received', (data) => {
      this.emitToHandlers('webhook_received', data);
    });

    this.socket.on('circuit_breaker_state_changed', (data) => {
      this.emitToHandlers('circuit_breaker_state_changed', data);
    });
  }

  // Emit event to all registered handlers
  private emitToHandlers(eventType: SocketEventType, data: any): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in ${eventType} handler:`, error);
        }
      });
    }
  }

  // Subscribe to a specific event
  on<T = any>(eventType: SocketEventType, handler: SocketEventHandler<T>): () => void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.add(handler);
    }

    // Return unsubscribe function
    return () => this.off(eventType, handler);
  }

  // Unsubscribe from a specific event
  off(eventType: SocketEventType, handler: SocketEventHandler): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  // Emit a custom event to the server
  emit(eventType: string, data: any): void {
    if (this.socket?.connected) {
      this.socket.emit(eventType, data);
    } else {
      console.warn('Socket not connected. Cannot emit event:', eventType);
    }
  }

  // Check if socket is connected
  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  // Get socket ID
  getSocketId(): string | undefined {
    return this.socket?.id;
  }
}

// Export singleton instance
export const socketManager = new SocketManager();

// Auto-connect helper
export function initializeSocket(): void {
  if (typeof window !== 'undefined' && AuthManager.isAuthenticated()) {
    socketManager.connect();
  }
}

// Auto-disconnect helper
export function cleanupSocket(): void {
  socketManager.disconnect();
}
