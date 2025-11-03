"""
Event Handler Decorators
Convenient decorators for registering event handlers
"""
from functools import wraps
from typing import Callable
import logging

from .event_bus import event_bus
from .base_event import BaseEvent

logger = logging.getLogger(__name__)


def event_handler(event_type: str, priority: int = 0):
    """
    Decorator to register a function as an event handler

    Args:
        event_type: Event type to listen for (e.g., 'sales.order.created')
                   Use '*' to listen to all events
        priority: Handler priority (higher = executed first)

    Example:
        @event_handler('sales.order.created')
        async def handle_order_created(event: BaseEvent):
            print(f"Order created: {event.data}")

        @event_handler('*')  # Listen to all events
        async def log_all_events(event: BaseEvent):
            print(f"Event: {event.event_type}")
    """
    def decorator(func: Callable):
        # Register the handler with the event bus
        event_bus.subscribe(event_type, func, priority=priority)

        # Store metadata on the function
        func._event_type = event_type
        func._priority = priority

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def on_event(event_type: str):
    """
    Simplified decorator for event handlers (alias for event_handler)

    Args:
        event_type: Event type to listen for

    Example:
        @on_event('inventory.stock.low')
        async def send_low_stock_alert(event: BaseEvent):
            product_id = event.data['product_id']
            # Send alert...
    """
    return event_handler(event_type, priority=0)


def event_middleware(func: Callable):
    """
    Decorator to register middleware

    Middleware runs before all event handlers.

    Example:
        @event_middleware
        def log_events(event: BaseEvent):
            print(f"Event: {event.event_type} at {event.timestamp}")
    """
    event_bus.add_middleware(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class EventHandlerRegistry:
    """
    Registry for managing event handlers

    Allows modules to register/unregister handlers programmatically
    """

    def __init__(self):
        self._handlers = {}

    def register(self, event_type: str, handler: Callable, priority: int = 0):
        """
        Register an event handler

        Args:
            event_type: Event type
            handler: Handler function
            priority: Handler priority
        """
        event_bus.subscribe(event_type, handler, priority)

        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)
        logger.info(f"Registered handler: {handler.__name__} for {event_type}")

    def unregister(self, event_type: str, handler: Callable):
        """
        Unregister an event handler

        Args:
            event_type: Event type
            handler: Handler function
        """
        event_bus.unsubscribe(event_type, handler)

        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
            logger.info(f"Unregistered handler: {handler.__name__} from {event_type}")

    def get_handlers(self, event_type: str) -> list:
        """Get all handlers for an event type"""
        return self._handlers.get(event_type, [])

    def clear(self):
        """Clear all registered handlers"""
        self._handlers.clear()
        logger.info("Cleared all handlers from registry")


# Global handler registry
handler_registry = EventHandlerRegistry()
