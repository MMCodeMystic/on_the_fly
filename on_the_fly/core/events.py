"""Einfacher Event-Bus für Entkopplung."""
from dataclasses import dataclass
from typing import Callable, Any
from enum import Enum, auto


class GameEvent(Enum):
    FLY_LANDED_ON_NPC = auto()
    FLY_DETACHED = auto()
    FLY_HIT = auto()
    FLY_ENTERED_DOOR = auto()
    FLY_REACHED_GOAL = auto()
    NPC_STARTED_CHASING = auto()
    NPC_REACTED = auto()
    DOOR_OPENED = auto()
    DOOR_CLOSED = auto()


@dataclass
class Event:
    type: GameEvent
    data: dict[str, Any] = None


class EventBus:
    def __init__(self):
        self._listeners: dict[GameEvent, list[Callable]] = {}

    def subscribe(self, event_type: GameEvent, callback: Callable):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def publish(self, event: Event):
        for cb in self._listeners.get(event.type, []):
            cb(event)