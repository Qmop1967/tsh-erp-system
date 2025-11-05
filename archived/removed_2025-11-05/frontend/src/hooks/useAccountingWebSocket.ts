import { useEffect, useRef, useCallback } from 'react'
import { toast } from 'react-hot-toast'

interface AccountingWebSocketMessage {
  event: string
  data: any
  timestamp: string
}

interface UseAccountingWebSocketProps {
  onJournalEntryCreated?: (entry: any) => void
  onJournalEntryUpdated?: (entry: any) => void
  onJournalEntryPosted?: (entryId: number) => void
  onSummaryUpdated?: (summary: any) => void
  enabled?: boolean
}

export const useAccountingWebSocket = ({
  onJournalEntryCreated,
  onJournalEntryUpdated,
  onJournalEntryPosted,
  onSummaryUpdated,
  enabled = true
}: UseAccountingWebSocketProps = {}) => {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 5

  const connect = useCallback(() => {
    if (!enabled) return

    // Use wss:// for production (https) or ws:// for development (http)
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.hostname}:8000/api/accounting/ws`

    console.log('Connecting to accounting WebSocket:', wsUrl)

    try {
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('✅ Accounting WebSocket connected')
        reconnectAttemptsRef.current = 0
        toast.success('Connected to real-time accounting updates', {
          duration: 2000,
          position: 'bottom-right',
        })
      }

      ws.onmessage = (event) => {
        try {
          const message: AccountingWebSocketMessage = JSON.parse(event.data)

          console.log('📨 Received accounting update:', message)

          switch (message.event) {
            case 'journal_entry_created':
              onJournalEntryCreated?.(message.data)
              toast.success('New journal entry created!', {
                duration: 3000,
                position: 'bottom-right',
              })
              break

            case 'journal_entry_updated':
              onJournalEntryUpdated?.(message.data)
              toast.info('Journal entry updated', {
                duration: 2000,
                position: 'bottom-right',
              })
              break

            case 'journal_entry_posted':
              onJournalEntryPosted?.(message.data.entry_id)
              toast.success('Journal entry posted!', {
                duration: 2000,
                position: 'bottom-right',
              })
              break

            case 'accounting_summary_updated':
              onSummaryUpdated?.(message.data)
              break

            default:
              console.log('Unknown event:', message.event)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('❌ Accounting WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('🔌 Accounting WebSocket disconnected')
        wsRef.current = null

        // Attempt to reconnect
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})...`)

          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, delay)
        } else {
          toast.error('Failed to connect to real-time updates', {
            duration: 5000,
            position: 'bottom-right',
          })
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
    }
  }, [enabled, onJournalEntryCreated, onJournalEntryUpdated, onJournalEntryPosted, onSummaryUpdated])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  useEffect(() => {
    if (enabled) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [enabled, connect, disconnect])

  return {
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
    reconnect: connect,
    disconnect
  }
}
