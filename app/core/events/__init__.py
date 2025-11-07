"""
Event-Driven Communication Infrastructure
Core event system for modular monolith architecture
"""
from .base_event import BaseEvent, DomainEvent
from .event_bus import EventBus, event_bus
from .handlers import event_handler, on_event
from .event_store import EventStore, event_store

__all__ = [
    "BaseEvent",
    "DomainEvent",
    "EventBus",
    "event_bus",
    "event_handler",
    "on_event",
    "EventStore",
    "event_store",
]
