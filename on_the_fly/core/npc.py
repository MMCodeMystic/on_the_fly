from dataclasses import dataclass, field
from enum import Enum, auto
from core.state import NPCState, NPCType
from typing import Optional


@dataclass
class Waypoint:
    pos: tuple[float, float]
    wait_time: float = 0.0
    door: str | None = None  # Wenn der NPC an diesem Punkt eine Tür öffnet


class NPCType(Enum):
    HUMAN = auto()
    DOG = auto()
    CAT = auto()
    CHILD = auto()


@dataclass
class NPC:
    name: str
    pos: tuple[float, float]
    npc_type: NPCType
    state: NPCState = NPCState.IDLE
    speed: float = 80.0
    chase_speed: float = 140.0
    route: list[Waypoint] = field(default_factory=list)
    route_index: int = 0
    wait_timer: float = 0.0
    reaction_radius: float = 100.0
    is_chasing: bool = False
    chase_timer: float = 0.0
    chase_duration: float = 3.0  # Wie lange der NPC jagt
    can_carry_fly: bool = True
    fly_attach_offset: tuple[float, float] = (0, -20)

    def update(self, dt: float, fly_pos: tuple[float, float] | None = None,
               doors: list | None = None):
        if self.state == NPCState.IDLE:
            self.wait_timer -= dt
            if self.wait_timer <= 0 and self.route:
                self.state = NPCState.WALKING
                # Tür-Check: Öffnet NPC eine Tür an diesem Waypoint?
                wp = self.route[self.route_index]
                if wp.door and doors:
                    for d in doors:
                        if d.name == wp.door:
                            d.open()
        elif self.state == NPCState.WALKING:
            target = self.route[self.route_index].pos
            dx = target[0] - self.pos[0]
            dy = target[1] - self.pos[1]
            dist = (dx**2 + dy**2) ** 0.5
            if dist < 3:
                self.route_index = (self.route_index + 1) % len(self.route)
                self.state = NPCState.IDLE
                self.wait_timer = self.route[self.route_index].wait_time
            else:
                self.pos = (
                    self.pos[0] + (dx / dist) * self.speed * dt,
                    self.pos[1] + (dy / dist) * self.speed * dt,
                )
        elif self.state == NPCState.CHASING:
            self.chase_timer -= dt
            if self.chase_timer <= 0:
                # Jagd vorbei → zurück zur Routine
                self.state = NPCState.WALKING
                self.is_chasing = False
                return
            # Auf Fliege zu bewegen
            if fly_pos:
                dx = fly_pos[0] - self.pos[0]
                dy = fly_pos[1] - self.pos[1]
                dist = (dx**2 + dy**2) ** 0.5
                if dist > 1:
                    self.pos = (
                        self.pos[0] + (dx / dist) * self.chase_speed * dt,
                        self.pos[1] + (dy / dist) * self.chase_speed * dt,
                    )
        elif self.state == NPCState.REACTING:
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                self.state = NPCState.WALKING

    def perceive_fly(self, fly_pos: tuple[float, float]) -> bool:
        dx = fly_pos[0] - self.pos[0]
        dy = fly_pos[1] - self.pos[1]
        return (dx**2 + dy**2) ** 0.5 < self.reaction_radius

    def start_chase(self):
        self.state = NPCState.CHASING
        self.is_chasing = True
        self.chase_timer = self.chase_duration   