"""
TSH ERP Accounting WebSocket Manager
Real-time updates for accounting events
"""

from fastapi import WebSocket
from typing import Dict, Set, List
import json
import asyncio
from datetime import datetime


class AccountingConnectionManager:
    """Manages WebSocket connections for accounting real-time updates"""

    def __init__(self):
        # Store active connections: {user_id: Set[WebSocket]}
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Store all connections for broadcast
        self.all_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, user_id: int = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.all_connections.add(websocket)

        if user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int = None):
        """Remove WebSocket connection"""
        self.all_connections.discard(websocket)

        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except:
            pass

    async def send_to_user(self, message: dict, user_id: int):
        """Send message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)

            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, user_id)

    async def broadcast(self, message: dict, exclude: WebSocket = None):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.all_connections:
            if connection != exclude:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_journal_entry_created(self, entry_data: dict):
        """Broadcast new journal entry creation"""
        message = {
            "event": "journal_entry_created",
            "data": entry_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)

    async def broadcast_journal_entry_updated(self, entry_data: dict):
        """Broadcast journal entry update"""
        message = {
            "event": "journal_entry_updated",
            "data": entry_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)

    async def broadcast_journal_entry_posted(self, entry_id: int):
        """Broadcast journal entry posted"""
        message = {
            "event": "journal_entry_posted",
            "data": {"entry_id": entry_id},
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)

    async def broadcast_accounting_summary_updated(self, summary_data: dict):
        """Broadcast accounting summary update"""
        message = {
            "event": "accounting_summary_updated",
            "data": summary_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)


# Global instance
accounting_ws_manager = AccountingConnectionManager()
