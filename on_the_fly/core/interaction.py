"""Interaktionssystem: Was kann die Fliege tun und was passiert?"""
from core.fly import Fly
from core.npc import NPC
from core.state import FlyState, NPCState, InteractionType
from core.events import EventBus, Event, GameEvent


class InteractionSystem:
    def __init__(self, event_bus: EventBus):
        self.bus = event_bus

    def try_land_on_npc(self, fly: Fly, npc: NPC) -> bool:
        """Fliege versucht auf NPC zu landen."""
        if not npc.can_carry_fly:
            return False
        if fly.state != FlyState.FREE_FLIGHT:
            return False
        # Distanz-Check (muss nahe genug sein)
        dx = fly.pos[0] - (npc.pos[0] + npc.fly_attach_offset[0])
        dy = fly.pos[1] - (npc.pos[1] + npc.fly_attach_offset[1])
        if (dx**2 + dy**2) ** 0.5 > 15:
            return False
        fly.attach(npc)
        self.bus.publish(Event(GameEvent.FLY_LANDED_ON_NPC, {"npc": npc.name}))
        return True

    def try_detach(self, fly: Fly) -> bool:
        """Fliege hebt ab."""
        if fly.state != FlyState.RIDING:
            return False
        fly.detach()
        self.bus.publish(Event(GameEvent.FLY_DETACHED, {}))
        return True

    def try_buzz(self, fly: Fly, target_npc: NPC) -> bool:
        """Fliege summt → NPC reagiert (dreht sich, lenkt ab)."""
        if fly.state != FlyState.FREE_FLIGHT:
            return False
        if not target_npc.perceive_fly(fly.pos):
            return False
        target_npc.state = NPCState.REACTING
        self.bus.publish(Event(GameEvent.NPC_REACTED, {"npc": target_npc.name}))
        return True

    def try_scare(self, fly: Fly, target_npc: NPC) -> bool:
        """Schneller Flug vor Gesicht → NPC weicht aus."""
        if fly.state != FlyState.FREE_FLIGHT:
            return False
        if fly.stamina < 20:
            return False
        fly.stamina -= 20
        # NPC weicht aus → kann Tür öffnen, etwas umstoßen
        target_npc.state = NPCState.REACTING
        self.bus.publish(Event(GameEvent.NPC_REACTED, {
            "npc": target_npc.name, "type": "scare"
        }))
        return True

    def check_chase(self, fly: Fly, npc: NPC) -> bool:
        if fly.state == FlyState.RIDING:
            return False
        if npc.state == NPCState.CHASING:
            return False  # Schon am jagen, nicht erneut triggern
        if npc.perceive_fly(fly.pos):
            npc.state = NPCState.CHASING
            npc.is_chasing = True
            npc.wait_timer = 1.0  # 1 Sekunde "Jagd", dann zurück zur Routine
            self.bus.publish(Event(GameEvent.NPC_STARTED_CHASING, {"npc": npc.name}))
            return True
        return False