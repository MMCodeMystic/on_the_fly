"""Abstrakte Renderer-Schnittstelle – austauschbar gegen Godot etc."""
from abc import ABC, abstractmethod
from core.level import Level
from core.fly import Fly
from core.npc import NPC
from core.room import Room


class BaseRenderer(ABC):
    @abstractmethod
    def init(self): ...

    @abstractmethod
    def draw_frame(self, level: Level, fly: Fly, dt: float): ...

    @abstractmethod
    def handle_input(self) -> tuple[float, float] | None:
        """Gibt normalisierte Eingabe-Richtung zurück oder None."""

    @abstractmethod
    def handle_action(self) -> str | None:
        """Gibt Action-Input zurück: 'land', 'detach', 'buzz', 'scare'."""

    @abstractmethod
    def quit(self): ...   