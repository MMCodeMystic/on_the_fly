from enum import Enum, auto


class FlyState(Enum):
    FREE_FLIGHT = auto()      # Fliegt frei, steuerbar
    RIDING = auto()            # Auf NPC (Schulter/Kopf)
    STUNNED = auto()           # Benommen (geschlagen)
    DEAD = auto()              # Game Over


class NPCState(Enum):
    IDLE = auto()
    WALKING = auto()
    REACTING = auto()          # Reagiert auf Fliege (dreht sich, schaut)
    CHASING = auto()           # Jagt die Fliege
    DOOR_TRANSIT = auto()      # Geht gerade durch Tür

class NPCType(Enum):
    HUMAN = auto()
    DOG = auto()
    CAT = auto()
    CHILD = auto()


class InteractionType(Enum):
    BUZZ = auto()              # Summen (Ablenkung)
    LAND_ON_NPC = auto()       # Auf NPC landen
    DETACH = auto()            # Abheben
    LAND_ON_OBJECT = auto()    # Auf Objekt landen (Krumme verschieben)
    SCARE = auto()             # Schneller Flug vor Gesicht