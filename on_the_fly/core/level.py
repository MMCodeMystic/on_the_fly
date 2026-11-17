from dataclasses import dataclass, field
from core.room import Room, Door
from core.npc import NPC
from core.fly import Fly
from core.state import FlyState
from typing import Optional
import json


@dataclass
class Level:
    rooms: dict[str, Room] = field(default_factory=dict)
    start_room: str = ""
    goal_room: str = ""
    fly: Optional[Fly] = None
    current_room_name: str = ""

    def add_room(self, room: Room):
        self.rooms[room.name] = room

    def get_current_room(self) -> Optional[Room]:
        return self.rooms.get(self.current_room_name)

    def update_doors(self, dt: float):
        """Türen schließen sich automatisch."""
        room = self.get_current_room()
        if room:
            for door in room.doors:
                door.update(dt)

    def check_door_transition(self) -> bool:
        """Fliege durchquert offene Tür → Raumwechsel."""
        room = self.get_current_room()
        if not room or not self.fly:
            return False
        if self.fly.state != FlyState.FREE_FLIGHT:
            return False  # Nur im Freiflug, nicht während Ride

        for door in room.doors:
            if not door.is_open:
                continue
            # Fliege in der Türöffnung?
            dx = abs(self.fly.pos[0] - door.pos[0])
            dy = abs(self.fly.pos[1] - door.pos[1])
            if dx < door.size[0] / 2 and dy < door.size[1] / 2:
                self._switch_room(door)
                return True
        return False

    def _switch_room(self, door: Door):
        """Raumwechsel: Fliege spawnen im Zielraum."""
        target = self.rooms.get(door.target_room)
        if not target:
            return
        # Gegenüberliegende Tür im Zielraum finden
        entry_door = None
        for d in target.doors:
            if d.target_room == self.current_room_name:
                entry_door = d
                break

        if entry_door:
            # Fliege kurz vor der Eingangstür spawnen
            self.fly.pos = (
                entry_door.pos[0] + (30 if entry_door.pos[0] == 0 else -30),
                entry_door.pos[1],
            )
        else:
            self.fly.pos = target.spawn_point

        self.current_room_name = door.target_room
        self.fly.vel = (0.0, 0.0)

    def clamp_fly_to_room(self):
        """Fliege im Raum halten."""
        room = self.get_current_room()
        if room and self.fly:
            self.fly.pos = (
                max(0, min(room.size[0], self.fly.pos[0])),
                max(0, min(room.size[1], self.fly.pos[1])),
            )

    @classmethod
    def from_json(cls, path: str) -> "Level":
        with open(path) as f:
            data = json.load(f)
        level = cls(
            start_room=data["start_room"],
            goal_room=data["goal_room"],
            current_room_name=data["start_room"],
        )
        for room_data in data["rooms"]:
            room = Room(
                name=room_data["name"],
                size=tuple(room_data["size"]),
                spawn_point=tuple(room_data.get("spawn", (50, 50))),
            )
            for door_data in room_data.get("doors", []):
                room.doors.append(Door(
                    name=door_data.get("name", f"{room_data['name']}_door"),
                    pos=tuple(door_data["pos"]),
                    size=tuple(door_data["size"]),
                    target_room=door_data["target"],
                    auto_close_time=door_data.get("auto_close_time", 4.0),
                ))
            for obs_data in room_data.get("obstacles", []):
                from core.room import Obstacle
                room.obstacles.append(Obstacle(
                    pos=tuple(obs_data["pos"]),
                    size=tuple(obs_data["size"]),
                    kind=obs_data.get("kind", "static"),
                ))
            level.add_room(room)
        return level   