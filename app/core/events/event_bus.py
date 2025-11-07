"""
Event Bus - In-Process Event Distribution
Handles publishing and subscribing to events within the monolith
"""
import asyncio
import logging
from typing import Callable, Dict, List, Set
from collections import defaultdict

from .base_event import BaseEvent

logger = logging.getLogger(__name__)


class EventBus:
    """
    In-process event bus for modular monolith

    Allows modules to communicate via events without direct dependencies.
    Supports both synchronous and asynchronous handlers.
    """

    def __init__(self):
        self._sync_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._async_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._wildcard_handlers: List[Callable] = []  # Handlers that listen to all events
        self._middleware: List[Callable] = []
        self._published_events: List[BaseEvent] = []  # For debugging/testing
        self._max_history: int = 1000

    def subscribe(self, event_type: str, handler: Callable, priority: int = 0):
        """
        Subscribe a handler to an event type

        Args:
            event_type: Event type to listen for (e.g., 'sales.order.created')
                       Use '*' to listen to all events
            handler: Function to call when event is published
            priority: Handler priority (higher = executed first)

        Example:
            @event_bus.subscribe('sales.order.created')
            async def handle_order(event):
                print(f"Order created: {event.data}")
        """
        if event_type == '*':
            self._wildcard_handlers.append(handler)
            logger.info(f"Registered wildcard handler: {handler.__name__}")
            return

        if asyncio.iscoroutinefunction(handler):
            self._async_handlers[event_type].append(handler)
            self._async_handlers[event_type].sort(
                key=lambda h: getattr(h, '_priority', 0),
                reverse=True
            )
            logger.info(f"Registered async handler for '{event_type}': {handler.__name__}")
        else:
            self._sync_handlers[event_type].append(handler)
            self._sync_handlers[event_type].sort(
                key=lambda h: getattr(h, '_priority', 0),
                reverse=True
            )
            logger.info(f"Registered sync handler for '{event_type}': {handler.__name__}")

    def unsubscribe(self, event_type: str, handler: Callable):
        """
        Unsubscribe a handler from an event type

        Args:
            event_type: Event type
            handler: Handler function to remove
        """
        if asyncio.iscoroutinefunction(handler):
            if event_type in self._async_handlers:
                self._async_handlers[event_type].remove(handler)
                logger.info(f"Unregistered async handler for '{event_type}': {handler.__name__}")
        else:
            if event_type in self._sync_handlers:
                self._sync_handlers[event_type].remove(handler)
                logger.info(f"Unregistered sync handler for '{event_type}': {handler.__name__}")

    async def publish(self, event: BaseEvent):
        """
        Publish an event to all subscribers

        Args:
            event: Event to publish

        The event will be delivered to:
        1. All handlers registered for this specific event type
        2. All wildcard handlers (registered with '*')
        """
        logger.info(f"Publishing event: {event.event_type} (id={event.event_id})")

        # Store event in history
        self._published_events.append(event)
        if len(self._published_events) > self._max_history:
            self._published_events.pop(0)

        # Run middleware
        for middleware in self._middleware:
            try:
                if asyncio.iscoroutinefunction(middleware):
                    await middleware(event)
                else:
                    middleware(event)
            except Exception as e:
                logger.error(f"Error in middleware: {e}", exc_info=True)

        event_type = event.event_type

        # Execute synchronous handlers
        for handler in self._sync_handlers.get(event_type, []):
            try:
                handler(event)
                logger.debug(f"Sync handler executed: {handler.__name__}")
            except Exception as e:
                logger.error(
                    f"Error in sync handler '{handler.__name__}' for event '{event_type}': {e}",
                    exc_info=True
                )

        # Execute asynchronous handlers
        async_tasks = []
        for handler in self._async_handlers.get(event_type, []):
            async_tasks.append(self._execute_async_handler(handler, event))

        # Execute wildcard handlers
        for handler in self._wildcard_handlers:
            if asyncio.iscoroutinefunction(handler):
                async_tasks.append(self._execute_async_handler(handler, event))
            else:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in wildcard handler: {e}", exc_info=True)

        # Wait for all async handlers to complete
        if async_tasks:
            results = await asyncio.gather(*async_tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Async handler failed: {result}", exc_info=result)

        logger.info(f"Event published successfully: {event.event_type}")

    async def _execute_async_handler(self, handler: Callable, event: BaseEvent):
        """
        Execute an async handler with error handling

        Args:
            handler: Async handler function
            event: Event to pass to handler
        """
        try:
            await handler(event)
            logger.debug(f"Async handler executed: {handler.__name__}")
        except Exception as e:
            logger.error(
                f"Error in async handler '{handler.__name__}' for event '{event.event_type}': {e}",
                exc_info=True
            )
            raise

    def add_middleware(self, middleware: Callable):
        """
        Add middleware to process events before delivery

        Middleware receives all events before handlers.

        Args:
            middleware: Function that receives event

        Example:
            def log_events(event):
                print(f"Event: {event.event_type}")

            event_bus.add_middleware(log_events)
        """
        self._middleware.append(middleware)
        logger.info(f"Added middleware: {middleware.__name__}")

    def get_handlers(self, event_type: str) -> Dict[str, List[str]]:
        """
        Get all handlers registered for an event type

        Args:
            event_type: Event type to query

        Returns:
            Dictionary with 'sync' and 'async' handler names
        """
        return {
            'sync': [h.__name__ for h in self._sync_handlers.get(event_type, [])],
            'async': [h.__name__ for h in self._async_handlers.get(event_type, [])],
            'wildcard': [h.__name__ for h in self._wildcard_handlers]
        }

    def get_event_history(self, limit: int = 100) -> List[BaseEvent]:
        """
        Get recent published events

        Args:
            limit: Maximum number of events to return

        Returns:
            List of recent events
        """
        return self._published_events[-limit:]

    def clear_history(self):
        """Clear event history"""
        self._published_events.clear()
        logger.info("Event history cleared")

    def get_stats(self) -> Dict[str, int]:
        """
        Get event bus statistics

        Returns:
            Dictionary with stats
        """
        return {
            'sync_handlers': sum(len(handlers) for handlers in self._sync_handlers.values()),
            'async_handlers': sum(len(handlers) for handlers in self._async_handlers.values()),
            'wildcard_handlers': len(self._wildcard_handlers),
            'middleware': len(self._middleware),
            'event_types': len(set(self._sync_handlers.keys()) | set(self._async_handlers.keys())),
            'events_published': len(self._published_events)
        }

    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"EventBus("
            f"handlers={stats['sync_handlers'] + stats['async_handlers']}, "
            f"event_types={stats['event_types']}, "
            f"events_published={stats['events_published']})"
        )


# Global event bus instance
event_bus = EventBus()
