from dataclasses import dataclass, field
from core.state import FlyState
from typing import Optional


@dataclass
class Fly:
    """Die Fliege – reines Datenmodell, kein Rendering."""
    pos: tuple[float, float]           # (x, y) in Weltkoordinaten
    vel: tuple[float, float] = (0.0, 0.0)
    state: FlyState = FlyState.FREE_FLIGHT
    rider: Optional["NPC"] = None      # Wer trägt mich gerade?
    stamina: float = 100.0             # Für schnelle Ausweichmanöver
    max_stamina: float = 100.0
    stun_timer: float = 0.0

    # Konstanten
    MAX_SPEED: float = 200.0           # px/s im Freiflug
    ACCELERATION: float = 500.0
    RIDING_SAFE_DISTANCE: float = 30.0 # Wie nah an Tür muss man sein zum Abheben

    def update(self, dt: float, input_dir: tuple[float, float] | None = None):
        """Ein Frame-Update. input_dir: normalisierte Richtung oder None."""
        if self.state == FlyState.STUNNED:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.state = FlyState.FREE_FLIGHT
            return

        if self.state == FlyState.FREE_FLIGHT:
            if input_dir:
                self.vel = (
                    input_dir[0] * self.MAX_SPEED,
                    input_dir[1] * self.MAX_SPEED,
                )
            else:
                self.vel = (0.0, 0.0)
            self.pos = (
                self.pos[0] + self.vel[0] * dt,
                self.pos[1] + self.vel[1] * dt,
            )
        elif self.state == FlyState.RIDING and self.rider:
            # Position folgt dem Rider
            self.pos = self.rider.pos

    def attach(self, npc: "NPC"):
        """Auf einen NPC aufsetzen."""
        self.rider = npc
        self.state = FlyState.RIDING
        self.pos = npc.pos

    def detach(self):
        """Abheben vom NPC."""
        self.rider = None
        self.state = FlyState.FREE_FLIGHT
        self.vel = (0.0, 0.0)

    def get_hit(self, stun_duration: float = 1.5):
        """Wird geschlagen."""
        self.state = FlyState.STUNNED
        self.stun_timer = stun_duration
        self.rider = None   