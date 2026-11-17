from dataclasses import dataclass, field


@dataclass
class Score:
    points: int = 0
    best: int = 0
    # Stats
    rooms_cleared: int = 0
    times_caught: int = 0
    doors_hit: int = 0
    chase_seconds: float = 0.0

    # Punktwerte
    PTS_CAUGHT: int = -50
    PTS_CLOSED_DOOR: int = -10
    PTS_CHASE_PER_SEC: int = 5
    PTS_ROOM_TRANSITION: int = 100

    def add(self, points: int):
        self.points += points
        if self.points > self.best:
            self.best = self.points

    def on_caught(self):
        self.times_caught += 1
        self.add(self.PTS_CAUGHT)

    def on_door_hit(self):
        self.doors_hit += 1
        self.add(self.PTS_CLOSED_DOOR)

    def on_chase_tick(self, dt: float):
        self.chase_seconds += dt
        # Punkte pro Sekunde (akkumulieren)
        self.points += int(self.PTS_CHASE_PER_SEC * dt)
        if self.points > self.best:
            self.best = self.points

    def on_room_transition(self):
        self.rooms_cleared += 1
        self.add(self.PTS_ROOM_TRANSITION)