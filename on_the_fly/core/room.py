from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Door:
    pos: tuple[float, float]
    size: tuple[float, float]  # (breite, höhe)
    target_room: str           # Name des Zielraums
    is_open: bool = False
    auto_close_time: float = 3.0  # Sekunden bis sich Tür schließt


@dataclass
class Obstacle:
    pos: tuple[float, float]
    size: tuple[float, float]
    kind: str = "static"  # "static", "fan", "trap", "glass"


@dataclass
class Room:
    name: str
    size: tuple[float, float]  # (breite, höhe)
    doors: list[Door] = field(default_factory=list)
    obstacles: list[Obstacle] = field(default_factory=list)
    npcs: list = field(default_factory=list)  # NPC-Instanzen
    spawn_point: tuple[float, float] = (50, 50)

    def contains(self, pos: tuple[float, float]) -> bool:
        x, y = pos
        return 0 <= x <= self.size[0] and 0 <= y <= self.size[1]

    def is_door_open(self, door: Door) -> bool:
        return door.is_open

@dataclass
class Door:
    name: str
    pos: tuple[float, float]
    size: tuple[float, float]
    target_room: str
    is_open: bool = False
    open_timer: float = 0.0
    auto_close_time: float = 4.0
    opened_by_npc: bool = True

    def open(self, duration: float = None):
        self.is_open = True
        self.open_timer = duration or self.auto_close_time

    def update(self, dt: float):
        if self.is_open:
            self.open_timer -= dt
            if self.open_timer <= 0:
                self.is_open = False

    def is_hit(self, pos: tuple[float, float]) -> bool:
        """Fliege berührt die Tür (nur wenn ZU)."""
        if self.is_open:
            return False
        dx = abs(pos[0] - self.pos[0])
        dy = abs(pos[1] - self.pos[1])
        return dx < self.size[0] / 2 + 5 and dy < self.size[1] / 2 + 5   