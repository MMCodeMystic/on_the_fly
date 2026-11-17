"""
On the Fly! – Entry Point
Läuft lokal (pygame) und im Browser (pygbag).
"""
import asyncio
import sys
from pathlib import Path

# Core (reine Logik)
from core.fly import Fly
from core.level import Level
from core.npc import NPC, Waypoint, NPCType
from core.room import Room, Door
from core.state import FlyState, NPCState
from core.events import EventBus, Event, GameEvent
from core.interaction import InteractionSystem
from core.scoring import Score

# Renderer (austauschbar)
from renderer.pygame_renderer import PygameRenderer


def build_test_level() -> Level:
    from core.state import NPCType

    level = Level(start_room="kitchen", goal_room="living",
                  current_room_name="kitchen")

    # Küche
    kitchen = Room(name="kitchen", size=(400, 300), spawn_point=(50, 150))
    kitchen.doors.append(Door(
        name="kitchen_door",
        pos=(400, 150), size=(30, 80),
        target_room="living", is_open=False,
        auto_close_time=4.0,
    ))
    # Hans geht zur Tür und öffnet sie
    human = NPC(
        name="Hans", pos=(100, 150),
        npc_type=NPCType.HUMAN,
        speed=60, chase_speed=130,
        chase_duration=2.5,
        reaction_radius=80,
        route=[
            Waypoint((100, 150), wait_time=1.0),
            Waypoint((380, 150), wait_time=0.5, door="kitchen_door"),  # ← Tür öffnen
            Waypoint((100, 150), wait_time=3.0),
        ],
    )
    kitchen.npcs.append(human)
    level.add_room(kitchen)

    # Wohnzimmer
    living = Room(name="living", size=(400, 300), spawn_point=(350, 150))
    living.doors.append(Door(
        name="living_door",
        pos=(0, 150), size=(30, 80),
        target_room="kitchen", is_open=False,
        auto_close_time=4.0,
    ))
    # Maria im Wohnzimmer
    maria = NPC(
        name="Maria", pos=(200, 150),
        npc_type=NPCType.HUMAN,
        speed=55, chase_speed=120,
        chase_duration=3.0,
        reaction_radius=70,
        route=[
            Waypoint((200, 150), wait_time=2.0),
            Waypoint((30, 150), wait_time=0.5, door="living_door"),
            Waypoint((300, 150), wait_time=2.0),
            Waypoint((200, 150), wait_time=1.0),
        ],
    )
    living.npcs.append(maria)
    level.add_room(living)

    level.fly = Fly(pos=(50, 150))
    return level


async def main():
    renderer = PygameRenderer()
    renderer.init()

    level = build_test_level()
    event_bus = EventBus()
    interactions = InteractionSystem(event_bus)
    score = Score()

    running = True
    while running:
        dt = 1 / 60

        direction = renderer.handle_input()
        action = renderer.handle_action()

        if action == "quit":
            running = False
            break

        level.fly.update(dt, direction)
        room = level.get_current_room()

        if room:
            # NPCs
            for npc in room.npcs:
                npc.update(dt, fly_pos=level.fly.pos, doors=room.doors)

            # Jagd-Check + Score
            chasing = False
            if level.fly.state == FlyState.FREE_FLIGHT:
                for npc in room.npcs:
                    if not npc.is_chasing and npc.perceive_fly(level.fly.pos):
                        npc.start_chase()
                        print(f"🏃 {npc.name} jagt!")

                    if npc.is_chasing:
                        chasing = True
                        dx = level.fly.pos[0] - npc.pos[0]
                        dy = level.fly.pos[1] - npc.pos[1]
                        if (dx**2 + dy**2) ** 0.5 < 20:
                            level.fly.get_hit()
                            npc.is_chasing = False
                            npc.state = NPCState.WALKING
                            score.on_caught()
                            print(f"💥 -{abs(score.PTS_CAUGHT)} Punkte")

            # Jagd-Punkte (Überleben)
            if chasing and level.fly.state == FlyState.FREE_FLIGHT:
                score.on_chase_tick(dt)

            # Tür-Treffer (geschlossene Tür)
            for door in room.doors:
                if door.is_hit(level.fly.pos):
                    score.on_door_hit()
                    # Fliege abprallen
                    level.fly.pos = (
                        level.fly.pos[0] - (1 if level.fly.pos[0] < door.pos[0] else -1) * 10,
                        level.fly.pos[1],
                    )
                    print(f"🚫 Tür! -{abs(score.PTS_CLOSED_DOOR)} Punkte")

            # Türen aktualisieren
            level.update_doors(dt)

            # Raumwechsel
            if level.check_door_transition():
                score.on_room_transition()
                print(f"➡️  {level.current_room_name}! +{score.PTS_ROOM_TRANSITION} Punkte")

        level.clamp_fly_to_room()

        # Aktionen
        if action and room:
            nearest_npc = _find_nearest_npc(level.fly, room.npcs, radius=50)
            if action == "land" and nearest_npc:
                interactions.try_land_on_npc(level.fly, nearest_npc)
            elif action == "detach":
                interactions.try_detach(level.fly)
            elif action == "buzz" and nearest_npc:
                interactions.try_buzz(level.fly, nearest_npc)
            elif action == "scare" and nearest_npc:
                interactions.try_scare(level.fly, nearest_npc)

        renderer.draw_frame(level, level.fly, dt, score)
        await asyncio.sleep(0)

    renderer.quit()


def _find_nearest_npc(fly: Fly, npcs: list, radius: float = 50):
    best = None
    best_dist = radius
    for npc in npcs:
        dx = fly.pos[0] - npc.pos[0]
        dy = fly.pos[1] - npc.pos[1]
        d = (dx**2 + dy**2) ** 0.5
        if d < best_dist:
            best = npc
            best_dist = d
    return best


if __name__ == "__main__":
    asyncio.run(main())