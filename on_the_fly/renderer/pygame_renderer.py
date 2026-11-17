import pygame
import sys
from renderer.base import BaseRenderer
from core.level import Level
from core.fly import Fly
from core.npc import NPC
from core.room import Room
from core.state import FlyState, NPCState


class PygameRenderer(BaseRenderer):
    SCALE = 1  # Weltkoordinaten → Pixel

    def __init__(self, width=960, height=640, fps=60):
        self.width = width
        self.height = height
        self.fps = fps
        self.screen = None
        self.clock = None

    def init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("On the Fly!")
        self.clock = pygame.time.Clock()

    def draw_frame(self, level: Level, fly: Fly, dt: float):
        self.screen.fill((30, 30, 40))

        # Aktuellen Raum zeichnen
        room = level.get_current_room()
        if room:
            self._draw_room(room)

        # NPCs zeichnen
        for npc in room.npcs if room else []:
            self._draw_npc(npc)

        # Fliege zeichnen
        self._draw_fly(fly)

        pygame.display.flip()
        self.clock.tick(self.fps)

    def _draw_room(self, room: Room):
        rect = pygame.Rect(0, 0, room.size[0], room.size[1])
        pygame.draw.rect(self.screen, (60, 60, 80), rect)
        pygame.draw.rect(self.screen, (100, 100, 120), rect, 2)

        for door in room.doors:
            color = (0, 200, 0) if door.is_open else (200, 50, 50)
            drect = pygame.Rect(
                door.pos[0] - door.size[0] // 2,
                door.pos[1] - door.size[1] // 2,
                door.size[0], door.size[1],
            )
            pygame.draw.rect(self.screen, color, drect)
            # Timer anzeigen, wenn Tür offen
            if door.is_open:
                font = pygame.font.SysFont(None, 14)
                t = font.render(f"{door.open_timer:.1f}s", True, (255, 255, 0))
                self.screen.blit(t, (drect.centerx - t.get_width() // 2,
                                     drect.top - 18))

        for obs in room.obstacles:
            orect = pygame.Rect(
                obs.pos[0] - obs.size[0] // 2,
                obs.pos[1] - obs.size[1] // 2,
                obs.size[0], obs.size[1],
            )
            pygame.draw.rect(self.screen, (150, 100, 50), orect)

    def _draw_npc(self, npc: NPC):
        colors = {
            "human": (70, 130, 180),
            "dog": (180, 130, 70),
            "cat": (150, 150, 150),
            "child": (100, 180, 100),
        }
        color = colors.get(npc.npc_type.name.lower(), (200, 200, 200))
        if npc.state == NPCState.CHASING:
            color = (255, 50, 50)

        rect = pygame.Rect(npc.pos[0] - 15, npc.pos[1] - 25, 30, 50)
        pygame.draw.rect(self.screen, color, rect)
        # Name
        font = pygame.font.SysFont(None, 16)
        label = font.render(npc.name, True, (255, 255, 255))
        self.screen.blit(label, (npc.pos[0] - label.get_width() // 2, npc.pos[1] - 40))

    def _draw_fly(self, fly: Fly):
        color = {
            FlyState.FREE_FLIGHT: (255, 255, 0),
            FlyState.RIDING: (0, 255, 255),
            FlyState.STUNNED: (128, 128, 128),
        }.get(fly.state, (255, 0, 0))
        pygame.draw.circle(self.screen, color, (int(fly.pos[0]), int(fly.pos[1])), 5)

    def handle_input(self) -> tuple[float, float] | None:
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        if dx == 0 and dy == 0:
            return None
        length = (dx**2 + dy**2) ** 0.5
        return (dx / length, dy / length)

    def handle_action(self) -> str | None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "land"       # Auf NPC landen
                if event.key == pygame.K_LSHIFT:
                    return "detach"     # Abheben
                if event.key == pygame.K_e:
                    return "buzz"       # Summen
                if event.key == pygame.K_q:
                    return "scare"      # Schrecken
        return None

    def quit(self):
        pygame.quit()
        sys.exit()