"""
Socket.IO Server for TDS Real-Time Updates

Handles WebSocket connections for the TDS Admin Dashboard.
Provides real-time notifications for sync operations, alerts, and system health.
"""

import socketio
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI
from datetime import datetime

# Import JWT authentication utilities
# These would be imported from your auth module
# from app.auth.jwt import decode_token

logger = logging.getLogger(__name__)

# Create Socket.IO server instance
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # Configure based on your security requirements
    logger=True,
    engineio_logger=False,
)

# Track connected clients
connected_clients: Dict[str, Dict[str, Any]] = {}


@sio.event
async def connect(sid: str, environ: dict, auth: Optional[dict] = None):
    """
    Handle client connection.

    Args:
        sid: Socket ID
        environ: WSGI environment
        auth: Authentication data (should contain JWT token)
    """
    logger.info(f"Client attempting to connect: {sid}")

    # Verify authentication
    if not auth or 'token' not in auth:
        logger.warning(f"Client {sid} attempted to connect without authentication")
        await sio.disconnect(sid)
        return False

    token = auth.get('token')

    # TODO: Implement JWT token verification
    # try:
    #     user_data = decode_token(token)
    # except Exception as e:
    #     logger.error(f"Invalid token for client {sid}: {e}")
    #     await sio.disconnect(sid)
    #     return False

    # For now, accept all connections (REMOVE THIS IN PRODUCTION)
    # In production, verify the JWT token and extract user information
    user_data = {"user_id": "admin", "username": "admin"}  # Placeholder

    # Store client information
    connected_clients[sid] = {
        "user_data": user_data,
        "connected_at": datetime.utcnow().isoformat(),
    }

    logger.info(f"Client connected: {sid} (User: {user_data.get('username')})")

    # Send welcome message
    await sio.emit('connected', {
        'message': 'Connected to TDS Admin Dashboard',
        'timestamp': datetime.utcnow().isoformat(),
    }, room=sid)

    return True


@sio.event
async def disconnect(sid: str):
    """
    Handle client disconnection.

    Args:
        sid: Socket ID
    """
    client_info = connected_clients.pop(sid, None)
    if client_info:
        logger.info(f"Client disconnected: {sid} (User: {client_info.get('user_data', {}).get('username')})")
    else:
        logger.info(f"Unknown client disconnected: {sid}")


@sio.event
async def ping(sid: str):
    """
    Handle ping from client (health check).

    Args:
        sid: Socket ID
    """
    await sio.emit('pong', {'timestamp': datetime.utcnow().isoformat()}, room=sid)


def init_socketio(app: FastAPI) -> socketio.ASGIApp:
    """
    Initialize Socket.IO with FastAPI application.

    Args:
        app: FastAPI application instance

    Returns:
        Socket.IO ASGI application wrapper
    """
    # Wrap the FastAPI app with Socket.IO
    socket_app = socketio.ASGIApp(
        socketio_server=sio,
        other_asgi_app=app,
        socketio_path='/socket.io'
    )

    logger.info("Socket.IO server initialized")
    return socket_app


async def emit_event(event_type: str, data: Dict[str, Any], room: Optional[str] = None):
    """
    Emit an event to all connected clients or a specific room.

    Args:
        event_type: Type of event to emit
        data: Event data
        room: Optional room ID (socket ID) to emit to specific client
    """
    try:
        if room:
            await sio.emit(event_type, data, room=room)
            logger.debug(f"Emitted {event_type} to room {room}")
        else:
            await sio.emit(event_type, data)
            logger.debug(f"Broadcasted {event_type} to all clients ({len(connected_clients)} connected)")
    except Exception as e:
        logger.error(f"Error emitting {event_type}: {e}", exc_info=True)


def get_connected_clients_count() -> int:
    """
    Get the number of currently connected clients.

    Returns:
        Number of connected clients
    """
    return len(connected_clients)
