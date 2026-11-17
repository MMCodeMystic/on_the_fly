import pygame
import sys
import math
from renderer.base import BaseRenderer
from core.level import Level
from core.fly import Fly
from core.npc import NPC
from core.room import Room
from core.state import FlyState, NPCState
from core.scoring import Score


# Farbpalette
class C:
    BG = (22, 24, 35)
    WALL = (50, 52, 70)
    FLOOR = (40, 42, 58)
    DOOR_OPEN = (80, 200, 120)
    DOOR_CLOSED = (180, 60, 60)
    DOOR_FRAME = (80, 60, 40)
    HUMAN = (70, 130, 180)
    HUMAN_CHASE = (220, 60, 60)
    DOG = (180, 130, 70)
    CAT = (160, 160, 170)
    CHILD = (100, 190, 100)
    FLY_FREE = (255, 255, 80)
    FLY_RIDING = (80, 255, 255)
    FLY_STUNNED = (120, 120, 130)
    OBSTACLE = (120, 90, 50)
    HUD_BG = (15, 15, 25)
    HUD_TEXT = (240, 240, 255)
    HUD_SCORE = (255, 220, 80)
    HUD_RED = (255, 80, 80)
    HUD_GREEN = (80, 220, 120)


class PygameRenderer(BaseRenderer):
    def __init__(self, width=960, height=640, fps=60):
        self.width = width
        self.height = height
        self.fps = fps
        self.screen = None
        self.clock = None
        self._wing_phase = 0.0  # Flügelschlag-Animation

    def init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("🪰 On the Fly!")
        self.clock = pygame.time.Clock()
        self._font_small = pygame.font.SysFont("consolas", 14)
        self._font_med = pygame.font.SysFont("consolas", 18)
        self._font_large = pygame.font.SysFont("consolas", 28, bold=True)

    def draw_frame(self, level: Level, fly: Fly, dt: float, score: Score = None):
        self._wing_phase += dt * 30  # Flügelschlag

        self.screen.fill(C.BG)
        room = level.get_current_room()
        if room:
            self._draw_room(room)
            for npc in room.npcs:
                self._draw_npc(npc)
        self._draw_fly(fly, dt)
        if score:
            self._draw_hud(score, level)

        pygame.display.flip()
        self.clock.tick(self.fps)

    def _draw_room(self, room: Room):
        # Boden mit leichtem Verlauf
        for i in range(0, room.size[1], 4):
            shade = 40 + int(10 * math.sin(i / 60))
            pygame.draw.line(self.screen, (shade, shade, shade + 10),
                             (0, i), (room.size[0], i))

        # Wände (Rahmen)
        pygame.draw.rect(self.screen, C.WALL,
                         (0, 0, room.size[0], room.size[1]), 4)

        # Türen
        for door in room.doors:
            self._draw_door(door)

        # Hindernisse
        for obs in room.obstacles:
            rect = pygame.Rect(
                int(obs.pos[0] - obs.size[0] / 2),
                int(obs.pos[1] - obs.size[1] / 2),
                int(obs.size[0]), int(obs.size[1]),
            )
            pygame.draw.rect(self.screen, C.OBSTACLE, rect, border_radius=4)
            pygame.draw.rect(self.screen, (90, 65, 35), rect, 1, border_radius=4)

    def _draw_door(self, door):
        x, y = int(door.pos[0]), int(door.pos[1])
        w, h = int(door.size[0]), int(door.size[1])
        drect = pygame.Rect(x - w // 2, y - h // 2, w, h)

        # Rahmen
        frame = drect.inflate(8, 8)
        pygame.draw.rect(self.screen, C.DOOR_FRAME, frame, border_radius=3)

        # Türblatt
        color = C.DOOR_OPEN if door.is_open else C.DOOR_CLOSED
        pygame.draw.rect(self.screen, color, drect, border_radius=2)

        # Türgriff
        pygame.draw.circle(self.screen, (200, 200, 210),
                          (drect.right - 8, drect.centery), 3)

        # Countdown bei offener Tür
        if door.is_open:
            txt = self._font_small.render(f"{door.open_timer:.1f}s", True, C.HUD_SCORE)
            self.screen.blit(txt, (drect.centerx - txt.get_width() // 2, drect.top - 20))

    def _draw_npc(self, npc: NPC):
        x, y = int(npc.pos[0]), int(npc.pos[1])
        w, h = 32, 52

        # Farbe
        if npc.is_chasing:
            body_color = C.HUMAN_CHASE
        elif npc.npc_type.name == "HUMAN":
            body_color = C.HUMAN
        elif npc.npc_type.name == "DOG":
            body_color = C.DOG
        elif npc.npc_type.name == "CAT":
            body_color = C.CAT
        else:
            body_color = C.CHILD

        # Körper (abgerundetes Rechteck)
        body = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(self.screen, body_color, body, border_radius=8)
        pygame.draw.rect(self.screen, (0, 0, 0), body, 1, border_radius=8)

        # Kopf
        head_r = 10
        pygame.draw.circle(self.screen, (220, 190, 160), (x, y - h // 2 - 6), head_r)

        # Jagd-Indikator (Ausrufezeichen)
        if npc.is_chasing:
            txt = self._font_large.render("!", True, C.HUD_RED)
            self.screen.blit(txt, (x - txt.get_width() // 2, y - h // 2 - 35))
            # Roter Puls-Ring
            pulse = int(5 * math.sin(self._wing_phase * 0.5))
            pygame.draw.circle(self.screen, C.HUMAN_CHASE, (x, y), 30 + pulse, 2)

        # Name
        name_txt = self._font_small.render(npc.name, True, C.HUD_TEXT)
        self.screen.blit(name_txt, (x - name_txt.get_width() // 2, y + h // 2 + 4))

    def _draw_fly(self, fly: Fly, dt: float):
        x, y = int(fly.pos[0]), int(fly.pos[1])

        color = {
            FlyState.FREE_FLIGHT: C.FLY_FREE,
            FlyState.RIDING: C.FLY_RIDING,
            FlyState.STUNNED: C.FLY_STUNNED,
        }.get(fly.state, (255, 0, 0))

        # Körper
        pygame.draw.ellipse(self.screen, color, (x - 5, y - 3, 10, 6))

        # Flügel (animiert)
        if fly.state == FlyState.FREE_FLIGHT:
            wing_angle = math.sin(self._wing_phase) * 0.4
            wing_len = 7
            # Linke Flügel
            lx = int(x - 3 - wing_len * math.cos(wing_angle))
            ly = int(y - 4 - wing_len * math.sin(wing_angle))
            pygame.draw.line(self.screen, (200, 200, 255), (x - 3, y - 3), (lx, ly), 2)
            # Rechte Flügel
            rx = int(x + 3 + wing_len * math.cos(wing_angle))
            ry = int(y - 4 - wing_len * math.sin(wing_angle))
            pygame.draw.line(self.screen, (200, 200, 255), (x + 3, y - 3), (rx, ry), 2)

        # Stun-Effekt (Sterne)
        if fly.state == FlyState.STUNNED:
            for i in range(3):
                angle = self._wing_phase * 0.3 + i * 2.1
                sx = int(x + 12 * math.cos(angle))
                sy = int(y - 12 + 5 * math.sin(angle))
                pygame.draw.circle(self.screen, (255, 255, 100), (sx, sy), 2)

    def _draw_hud(self, score: Score, level: Level):
        # HUD-Hintergrund
        hud = pygame.Rect(0, 0, self.width, 36)
        surf = pygame.Surface((self.width, 36), pygame.SRCALPHA)
        surf.fill((*C.HUD_BG, 200))
        self.screen.blit(surf, (0, 0))
        pygame.draw.line(self.screen, (60, 60, 80), (0, 36), (self.width, 36))

        # Score
        score_txt = self._font_med.render(f"Score: {score.points}", True, C.HUD_SCORE)
        self.screen.blit(score_txt, (10, 8))

        # Best
        best_txt = self._font_small.render(f"Best: {score.best}", True, C.HUD_TEXT)
        self.screen.blit(best_txt, (140, 10))

        # Raum
        room_txt = self._font_small.render(f"Raum: {level.current_room_name}", True, C.HUD_TEXT)
        self.screen.blit(room_txt, (260, 10))

        # Stats rechts
        stats = f"🚪 {score.rooms_cleared}  💥 {score.times_caught}  🚫 {score.doors_hit}"
        stats_txt = self._font_small.render(stats, True, C.HUD_TEXT)
        self.screen.blit(stats_txt, (self.width - stats_txt.get_width() - 10, 10))

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
                    return "land"
                if event.key == pygame.K_LSHIFT:
                    return "detach"
                if event.key == pygame.K_e:
                    return "buzz"
                if event.key == pygame.K_q:
                    return "scare"
        return None

    def quit(self):
        pygame.quit()
        sys.exit()