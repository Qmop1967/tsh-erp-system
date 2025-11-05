import { useEffect, useRef, useCallback, useState } from 'react';
import type { Notification } from '../types/notification';

interface UseNotificationWebSocketOptions {
  userId: number;
  onNotification?: (notification: Notification) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

interface UseNotificationWebSocketReturn {
  isConnected: boolean;
  reconnect: () => void;
  disconnect: () => void;
}

const useNotificationWebSocket = ({
  userId,
  onNotification,
  onConnect,
  onDisconnect,
  onError,
  autoReconnect = true,
  reconnectInterval = 5000,
}: UseNotificationWebSocketOptions): UseNotificationWebSocketReturn => {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldConnectRef = useRef(true);

  const connect = useCallback(() => {
    if (!shouldConnectRef.current) return;

    // Determine WebSocket URL based on current location
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = '8000'; // Backend port
    const wsUrl = `${protocol}//${host}:${port}/api/v1/notifications/ws/${userId}`;

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        setIsConnected(true);
        if (onConnect) onConnect();

        // Clear any pending reconnect attempts
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'notification' && onNotification) {
            onNotification(data.notification);
          } else if (data.type === 'ping') {
            // Respond to ping to keep connection alive
            ws.send(JSON.stringify({ type: 'pong' }));
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        if (onError) onError(error);
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        setIsConnected(false);
        wsRef.current = null;
        if (onDisconnect) onDisconnect();

        // Auto-reconnect if enabled and component is still mounted
        if (autoReconnect && shouldConnectRef.current) {
          console.log(`🔄 Reconnecting in ${reconnectInterval}ms...`);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [userId, onNotification, onConnect, onDisconnect, onError, autoReconnect, reconnectInterval]);

  const disconnect = useCallback(() => {
    shouldConnectRef.current = false;

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    shouldConnectRef.current = true;
    connect();
  }, [connect, disconnect]);

  // Connect on mount
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    reconnect,
    disconnect,
  };
};

export default useNotificationWebSocket;
