import pygame
import random
import math
import sys
import json
import os
import colorsys


pygame.init()

WIDTH, HEIGHT = 800, 600
display_surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bucket Star Catcher")
screen = pygame.Surface((WIDTH, HEIGHT))  # everything is drawn here, then blitted with shake offset
clock = pygame.time.Clock()
FPS = 60

font_big = pygame.font.SysFont("arial", 60, bold=True)
font_med = pygame.font.SysFont("arial", 30, bold=True)
font_small = pygame.font.SysFont("arial", 20)
font_tiny = pygame.font.SysFont("arial", 16)

WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
SKY_TOP = (10, 10, 40)
SKY_BOTTOM = (40, 20, 70)
RED = (255, 80, 80)
GREEN = (100, 255, 150)
BLACK = (0, 0, 0)

HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.json")

def load_highscores():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_highscore(name, score):
    scores = load_highscores()
    scores.append({"name": name if name.strip() else "Player", "score": score})
    scores.sort(key=lambda e: e["score"], reverse=True)
    scores = scores[:10]
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(scores, f)
    except Exception:
        pass
    return scores


highscores = load_highscores()

def draw_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))


def draw_vertical_gradient_rect(surface, rect, top_color, bottom_color, border_radius=0):
    temp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        ratio = y / max(1, rect.height)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(temp, (r, g, b), (0, y), (rect.width, y))
    mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=border_radius)
    temp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(temp, rect.topleft)


def draw_text_shadow(surface, text, font, color, pos, shadow_color=(0, 0, 0)):
    x, y = pos
    shadow = font.render(text, True, shadow_color)
    surface.blit(shadow, (x + 3, y + 3))
    main = font.render(text, True, color)
    surface.blit(main, (x, y))


def draw_button(surface, rect, text, hover, base_color=(200, 160, 30), hover_color=(255, 215, 0)):
    color = hover_color if hover else base_color
    pygame.draw.rect(surface, color, rect, border_radius=14)
    pygame.draw.rect(surface, WHITE, rect, 3, border_radius=14)
    label = font_med.render(text, True, (25, 15, 0))
    surface.blit(label, (rect.centerx - label.get_width() // 2,
                          rect.centery - label.get_height() // 2))


shake_timer = 0
shake_mag = 0


def trigger_shake(magnitude=8, duration=10):
    global shake_timer, shake_mag
    shake_timer = duration
    shake_mag = magnitude


def get_shake_offset():
    global shake_timer
    if shake_timer > 0:
        shake_timer -= 1
        return (random.randint(-shake_mag, shake_mag), random.randint(-shake_mag, shake_mag))
    return (0, 0)


class CloudLayer:
    def __init__(self, speed, y, alpha, scale, count):
        self.speed = speed
        self.y = y
        self.alpha = alpha
        self.scale = scale
        self.clouds = [random.uniform(0, WIDTH) for _ in range(count)]

    def update(self):
        for i in range(len(self.clouds)):
            self.clouds[i] += self.speed
            if self.clouds[i] > WIDTH + 100:
                self.clouds[i] = -100

    def draw(self, surface):
        for cx in self.clouds:
            s = pygame.Surface((160 * self.scale, 60 * self.scale), pygame.SRCALPHA)
            col = (255, 255, 255, self.alpha)
            w, h = s.get_size()
            pygame.draw.ellipse(s, col, (0, h * 0.3, w * 0.6, h * 0.6))
            pygame.draw.ellipse(s, col, (w * 0.25, h * 0.05, w * 0.55, h * 0.7))
            pygame.draw.ellipse(s, col, (w * 0.45, h * 0.3, w * 0.55, h * 0.6))
            surface.blit(s, (cx, self.y))


cloud_layers = [
    CloudLayer(0.10, 70, 35, 1.0, 3),
    CloudLayer(0.22, 130, 55, 1.3, 3),
    CloudLayer(0.40, 190, 80, 0.8, 4),
]


def draw_moon(surface):
    mx, my, mr = WIDTH - 90, 90, 42
    glow = pygame.Surface((mr * 5, mr * 5), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 250, 200, 40), (mr * 2, mr * 2), int(mr * 2.2))
    surface.blit(glow, (mx - mr * 2, my - mr * 2))
    pygame.draw.circle(surface, (255, 250, 210), (mx, my), mr)
    pygame.draw.circle(surface, (230, 220, 180), (mx - 12, my - 8), 8)
    pygame.draw.circle(surface, (230, 220, 180), (mx + 10, my + 14), 10)


def draw_mountains(surface):
    layers = [
        ((30, 20, 55), HEIGHT - 40, 60),
        ((45, 28, 70), HEIGHT - 10, 90),
    ]
    for color, base_y, amp in layers:
        points = [(0, HEIGHT)]
        for x in range(0, WIDTH + 40, 40):
            y = base_y - abs(math.sin(x * 0.01 + color[0])) * amp
            points.append((x, y))
        points.append((WIDTH, HEIGHT))
        pygame.draw.polygon(surface, color, points)


class BackgroundStar:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT // 2)
        self.radius = random.uniform(0.5, 2)
        self.twinkle_speed = random.uniform(0.02, 0.08)
        self.phase = random.uniform(0, math.pi * 2)

    def update(self):
        self.phase += self.twinkle_speed

    def draw(self, surface):
        brightness = (math.sin(self.phase) + 1) / 2
        alpha = int(100 + brightness * 155)
        s = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, alpha), (3, 3), self.radius)
        surface.blit(s, (self.x - 3, self.y - 3))


bg_stars = [BackgroundStar() for _ in range(70)]


def draw_background():
    draw_gradient(screen, SKY_TOP, SKY_BOTTOM)
    draw_moon(screen)
    for bstar in bg_stars:
        bstar.update()
        bstar.draw(screen)
    for layer in cloud_layers:
        layer.update()
        layer.draw(screen)
    draw_mountains(screen)


def draw_star_shape(surface, center, size, color, glow=True):
    cx, cy = center
    points = []
    for i in range(10):
        angle = math.pi / 5 * i - math.pi / 2
        r = size if i % 2 == 0 else size * 0.45
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

    if glow:
        glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 60), (size * 2, size * 2), size * 1.8)
        surface.blit(glow_surf, (cx - size * 2, cy - size * 2))

    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, WHITE, points, 1)


STAR_TYPES = {
    "silver":  {"color": (210, 215, 230), "points": 5,  "speed_mult": 0.9, "weight": 40},
    "normal":  {"color": (255, 240, 150), "points": 10, "speed_mult": 1.0, "weight": 35},
    "gold":    {"color": (255, 215, 0),   "points": 25, "speed_mult": 1.1, "weight": 18},
    "rainbow": {"color": None,            "points": 50, "speed_mult": 1.25, "weight": 7},
}


def choose_star_type():
    types = list(STAR_TYPES.keys())
    weights = [STAR_TYPES[t]["weight"] for t in types]
    return random.choices(types, weights=weights, k=1)[0]


class FallingStar:
    def __init__(self, speed_mult=1.0):
        self.type = choose_star_type()
        info = STAR_TYPES[self.type]
        self.points = info["points"]
        self.base_color = info["color"]
        self.x = random.randint(30, WIDTH - 30)
        self.y = -30
        self.size = random.randint(14, 22)
        self.speed = random.uniform(2, 4) * speed_mult * info["speed_mult"]
        self.trail = []

    def get_color(self):
        if self.type == "rainbow":
            hue = (pygame.time.get_ticks() * 0.0006) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.75, 1.0)
            return (int(r * 255), int(g * 255), int(b * 255))
        return self.base_color

    def update(self, bucket_x=None, magnet_active=False, speed_scale=1.0):
        if magnet_active and bucket_x is not None:
            self.x += (bucket_x - self.x) * 0.045
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)
        self.y += self.speed * speed_scale

    def draw(self, surface):
        color = self.get_color()
        n = len(self.trail)
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(130 * (i / max(1, n)))
            r = max(1, self.size * 0.28 * (i / max(1, n)))
            s = pygame.Surface((int(r * 2) + 2, int(r * 2) + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (int(r) + 1, int(r) + 1), int(r))
            surface.blit(s, (tx - r, ty - r))
        draw_star_shape(surface, (self.x, self.y), self.size, color)

    def off_screen(self):
        return self.y > HEIGHT + 30

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)


class Obstacle:
    def __init__(self, speed_mult=1.0):
        self.x = random.randint(30, WIDTH - 30)
        self.y = -30
        self.size = random.randint(16, 23)
        self.speed = random.uniform(2.5, 4.3) * speed_mult
        self.trail = []

    def update(self, speed_scale=1.0):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)
        self.y += self.speed * speed_scale

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(90 * (i / max(1, len(self.trail))))
            r = max(1, self.size * 0.25 * (i / max(1, len(self.trail))))
            s = pygame.Surface((int(r * 2) + 2, int(r * 2) + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (60, 30, 30, alpha), (int(r) + 1, int(r) + 1), int(r))
            surface.blit(s, (tx - r, ty - r))

        pad = 12
        s = pygame.Surface((self.size * 2 + pad, self.size * 2 + pad), pygame.SRCALPHA)
        c = (self.size + pad // 2, self.size + pad // 2)
        pygame.draw.circle(s, (45, 45, 50), c, self.size)
        pygame.draw.circle(s, (15, 15, 18), c, self.size, 3)
        pygame.draw.circle(s, (90, 90, 95), (c[0] - self.size // 3, c[1] - self.size // 3), max(2, self.size // 4))
        fuse_end = (c[0] + 6, c[1] - self.size - 8)
        pygame.draw.line(s, (150, 100, 50), (c[0], c[1] - self.size), fuse_end, 3)
        spark = random.choice([(255, 150, 50), (255, 220, 100)])
        pygame.draw.circle(s, spark, fuse_end, 4)
        surface.blit(s, (self.x - c[0], self.y - c[1]))

    def off_screen(self):
        return self.y > HEIGHT + 30

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)


POWERUP_TYPES = ["magnet", "shield", "slow", "double", "heart"]
POWERUP_COLORS = {
    "magnet": (255, 110, 200),
    "shield": (110, 200, 255),
    "slow": (170, 255, 180),
    "double": (255, 220, 80),
    "heart": (255, 90, 90),
}
POWERUP_LABELS = {"magnet": "M", "shield": "S", "slow": "S-M", "double": "x2", "heart": "+1"}
POWERUP_NAMES = {"magnet": "Magnet", "shield": "Shield", "slow": "Slow-Mo", "double": "Double Pts", "heart": "Extra Life"}
POWERUP_DURATION = 8 * FPS  # frames
MAX_LIVES = 5
EXTRA_LIFE_STEP = 300  # score needed per bonus life from collecting stars


class PowerUp:
    def __init__(self, speed_mult=1.0):
        self.type = random.choice(POWERUP_TYPES)
        self.x = random.randint(30, WIDTH - 30)
        self.y = -30
        self.size = 17
        self.speed = random.uniform(2, 3) * speed_mult
        self.pulse = random.uniform(0, math.pi * 2)

    def update(self, speed_scale=1.0):
        self.y += self.speed * speed_scale
        self.pulse += 0.15

    def draw(self, surface):
        color = POWERUP_COLORS[self.type]
        glow_r = self.size + math.sin(self.pulse) * 4
        s = pygame.Surface((int(glow_r * 4), int(glow_r * 4)), pygame.SRCALPHA)
        cc = (int(glow_r * 2), int(glow_r * 2))
        pygame.draw.circle(s, (*color, 70), cc, int(glow_r * 1.8))

        if self.type == "heart":
            hs = self.size * 0.9
            lx, ly = cc[0] - hs * 0.5, cc[1] - hs * 0.25
            rx, ry = cc[0] + hs * 0.5, cc[1] - hs * 0.25
            pygame.draw.circle(s, color, (int(lx), int(ly)), int(hs * 0.5))
            pygame.draw.circle(s, color, (int(rx), int(ry)), int(hs * 0.5))
            tip = (cc[0], cc[1] + hs * 0.75)
            pygame.draw.polygon(s, color, [
                (cc[0] - hs * 0.95, cc[1] - hs * 0.1),
                (cc[0] + hs * 0.95, cc[1] - hs * 0.1),
                tip,
            ])
            pygame.draw.circle(s, WHITE, cc, self.size, 2)
        else:
            pygame.draw.circle(s, color, cc, self.size)
            pygame.draw.circle(s, WHITE, cc, self.size, 2)
            label = font_tiny.render(POWERUP_LABELS[self.type], True, (25, 20, 10))
            s.blit(label, (cc[0] - label.get_width() / 2, cc[1] - label.get_height() / 2))

        surface.blit(s, (self.x - cc[0], self.y - cc[1]))

    def off_screen(self):
        return self.y > HEIGHT + 30

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)


class Particle:
    def __init__(self, x, y, color, speed_range=(2, 6), life=30):
        self.x, self.y = x, y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(*speed_range)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = life
        self.max_life = life
        self.color = color
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha = max(0, int(255 * (self.life / self.max_life)))
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
            surface.blit(s, (self.x - self.size, self.y - self.size))


particles = []


def spawn_burst(x, y, color, count=18, speed_range=(2, 6), life=30):
    for _ in range(count):
        particles.append(Particle(x, y, color, speed_range, life))


BUCKET_SKINS = {
    "Wood":  {"top": (200, 130, 70),  "bottom": (120, 70, 35),  "rim": (215, 160, 95),  "outline": (80, 48, 22),  "handle": (150, 100, 55)},
    "Gold":  {"top": (255, 223, 120), "bottom": (185, 140, 40), "rim": (255, 240, 180), "outline": (120, 90, 20), "handle": (230, 190, 100)},
    "Ice":   {"top": (205, 240, 255), "bottom": (120, 180, 220), "rim": (230, 250, 255), "outline": (60, 100, 140), "handle": (170, 220, 240)},
    "Neon":  {"top": (255, 90, 220),  "bottom": (90, 25, 130),  "rim": (180, 255, 255), "outline": (255, 0, 180), "handle": (120, 255, 255)},
}
SKIN_NAMES = list(BUCKET_SKINS.keys())

DIFFICULTIES = ["Easy", "Medium", "Hard"]
DIFFICULTY_SETTINGS = {
    "Easy":   {"star_speed": 0.75, "obstacle_level": 3, "spawn_bonus": 10},
    "Medium": {"star_speed": 1.0,  "obstacle_level": 2, "spawn_bonus": 0},
    "Hard":   {"star_speed": 1.35, "obstacle_level": 1, "spawn_bonus": -10},
}


class Bucket:
    def __init__(self, skin="Wood"):
        self.width = 100
        self.height = 60
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 95
        self.base_speed = 9
        self.wobble = 0
        self.tilt = 0
        self.squash = 1.0
        self.squash_target = 1.0
        self.catch_flash = 0
        self.facing = 0
        self.skin = skin
        self.fill_display = 0.0
        self.fill_target = 0.0
        self.shrink = 1.0  

    def trigger_catch(self):
        self.squash = 1.25
        self.catch_flash = 12

    def update(self, keys, speed_scale=1.0):
        moving = False
        self.facing = 0
        speed = self.base_speed * speed_scale
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= speed
            moving = True
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += speed
            moving = True
            self.facing = 1
        eff_width = self.width * self.shrink
        self.x = max(0, min(WIDTH - eff_width, self.x))

        self.wobble = math.sin(pygame.time.get_ticks() * 0.012) * 3 if moving else 0
        target_tilt = self.facing * 6
        self.tilt += (target_tilt - self.tilt) * 0.2

        self.squash += (self.squash_target - self.squash) * 0.25
        if self.catch_flash > 0:
            self.catch_flash -= 1

        self.shrink += (1.0 - self.shrink) * 0.05
        self.fill_display += (self.fill_target - self.fill_display) * 0.08

    def get_rect(self):
        eff_width = self.width * self.shrink
        return pygame.Rect(self.x, self.y, eff_width, self.height)

    def draw(self, surface):
        colors = BUCKET_SKINS[self.skin]
        w_base = self.width * self.shrink
        h_base = self.height
        w = w_base * (1 + (self.squash - 1) * 0.5)
        h = h_base * (1 - (self.squash - 1) * 0.4)
        cx = self.x + w_base / 2
        top_y = self.y + (h_base - h)
        wobble = self.wobble
        tilt = self.tilt

        shadow_w = w + 20
        shadow = pygame.Surface((int(shadow_w), 16), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 90), shadow.get_rect())
        surface.blit(shadow, (cx - shadow_w / 2, self.y + h_base + 6))

        if self.catch_flash > 0:
            alpha = int(255 * (self.catch_flash / 12))
            ring_r = 55 + (12 - self.catch_flash) * 4
            ring = pygame.Surface((ring_r * 2, ring_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*GOLD, alpha), (ring_r, ring_r), ring_r, 4)
            surface.blit(ring, (cx - ring_r, top_y - ring_r + h / 2))

        left_x = cx - w / 2 + tilt
        right_x = cx + w / 2 + tilt
        top_left = (left_x + wobble, top_y)
        top_right = (right_x + wobble, top_y)
        bot_left = (cx - w * 0.38 + tilt * 1.3, top_y + h)
        bot_right = (cx + w * 0.38 + tilt * 1.3, top_y + h)
        body_points = [top_left, top_right, bot_right, bot_left]

        min_x = int(min(p[0] for p in body_points))
        max_x = int(max(p[0] for p in body_points))
        min_y = int(min(p[1] for p in body_points))
        max_y = int(max(p[1] for p in body_points))
        body_rect = pygame.Rect(min_x, min_y, max(1, max_x - min_x), max(1, max_y - min_y))

        body_surf = pygame.Surface((body_rect.width, body_rect.height), pygame.SRCALPHA)
        local_points = [(px - min_x, py - min_y) for px, py in body_points]
        draw_vertical_gradient_rect(body_surf, body_surf.get_rect(), colors["top"], colors["bottom"])
        mask = pygame.Surface((body_rect.width, body_rect.height), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), local_points)
        body_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        
        if self.fill_display > 0.01:
            fill_h = int((body_rect.height - 6) * self.fill_display)
            fill_rect = pygame.Rect(0, body_rect.height - fill_h, body_rect.width, fill_h)
            fill_surf = pygame.Surface((body_rect.width, body_rect.height), pygame.SRCALPHA)
            draw_vertical_gradient_rect(fill_surf, fill_rect, (255, 235, 150), GOLD)
            fill_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            body_surf.blit(fill_surf, (0, 0))

        surface.blit(body_surf, body_rect.topleft)

        for i in range(1, 5):
            t = i / 5
            sx_top = top_left[0] + (top_right[0] - top_left[0]) * t
            sx_bot = bot_left[0] + (bot_right[0] - bot_left[0]) * t
            pygame.draw.line(surface, colors["outline"], (sx_top, top_y + 3), (sx_bot, top_y + h - 3), 1)

        pygame.draw.polygon(surface, colors["outline"], body_points, 3)

        inner_rect = pygame.Rect(top_left[0] + w * 0.08, top_y - 2, w * 0.84, 14)
        inner_surf = pygame.Surface((max(1, inner_rect.width), inner_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(inner_surf, (30, 15, 5, 150), inner_surf.get_rect())
        surface.blit(inner_surf, inner_rect.topleft)

        rim_rect = pygame.Rect(left_x + wobble, top_y - 9, w, 18)
        pygame.draw.ellipse(surface, colors["rim"], rim_rect)
        pygame.draw.ellipse(surface, colors["outline"], rim_rect, 3)
        highlight_rect = pygame.Rect(rim_rect.x + w * 0.12, rim_rect.y + 2, w * 0.35, 6)
        hl_surf = pygame.Surface((max(1, highlight_rect.width), highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(hl_surf, (255, 255, 255, 140), hl_surf.get_rect())
        surface.blit(hl_surf, highlight_rect.topleft)

        handle_rect = pygame.Rect(cx - w * 0.32 + tilt, top_y - 30, w * 0.64, 34)
        pygame.draw.arc(surface, colors["outline"], handle_rect, math.radians(15), math.radians(165), 4)
        pygame.draw.arc(surface, colors["handle"], handle_rect, math.radians(15), math.radians(165), 2)

        for side in (-1, 1):
            rivet_x = cx + side * w * 0.42 + tilt
            rivet_y = top_y + 4
            pygame.draw.circle(surface, colors["outline"], (int(rivet_x), int(rivet_y)), 3)
            pygame.draw.circle(surface, colors["rim"], (int(rivet_x - 1), int(rivet_y - 1)), 1)

    def draw_shield(self, surface):
        cx = self.x + (self.width * self.shrink) / 2
        cy = self.y + self.height / 2
        r = 65 + math.sin(pygame.time.get_ticks() * 0.01) * 4
        s = pygame.Surface((int(r * 2), int(r * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (110, 200, 255, 70), (int(r), int(r)), int(r))
        pygame.draw.circle(s, (150, 220, 255, 180), (int(r), int(r)), int(r), 3)
        surface.blit(s, (cx - r, cy - r))


def draw_hud(surface, game):
    draw_text_shadow(surface, f"Score: {game['score']}", font_med, WHITE, (20, 15))
    draw_text_shadow(surface, f"Level: {game['level']}", font_med, WHITE, (WIDTH // 2 - 55, 15))
    draw_text_shadow(surface, game["difficulty"], font_tiny, (200, 200, 200), (WIDTH // 2 - 55, 48))

    for i in range(game["lives"]):
        hx = WIDTH - 40 - i * 35
        pygame.draw.circle(surface, RED, (hx, 25), 10)
        pygame.draw.circle(surface, RED, (hx + 12, 25), 10)
        pygame.draw.polygon(surface, RED, [(hx - 10, 30), (hx + 22, 30), (hx + 6, 50)])

    y_off = 55
    for ptype, remaining in game["active_powerups"].items():
        if remaining > 0:
            color = POWERUP_COLORS[ptype]
            pct = remaining / POWERUP_DURATION
            badge_rect = pygame.Rect(20, y_off, 150, 20)
            pygame.draw.rect(surface, (0, 0, 0, 120), badge_rect, border_radius=8)
            fill_rect = pygame.Rect(20, y_off, int(150 * pct), 20)
            pygame.draw.rect(surface, color, fill_rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, badge_rect, 2, border_radius=8)
            label = font_tiny.render(POWERUP_NAMES[ptype], True, BLACK)
            surface.blit(label, (badge_rect.x + 6, badge_rect.y + 2))
            y_off += 26

    if game["shield"]:
        label = font_tiny.render("SHIELD READY", True, (110, 200, 255))
        surface.blit(label, (20, y_off + 2))


player_name = "Player"
name_active = False
selected_skin_index = 0
selected_difficulty_index = 1  # Medium by default


def draw_highscore_panel(surface, rect, title="HIGH SCORES"):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 0, 0, 110), panel.get_rect(), border_radius=12)
    pygame.draw.rect(panel, GOLD, panel.get_rect(), 2, border_radius=12)
    surface.blit(panel, rect.topleft)
    draw_text_shadow(surface, title, font_small, GOLD, (rect.x + 14, rect.y + 10))
    top = load_highscores()[:5]
    if not top:
        draw_text_shadow(surface, "No scores yet", font_tiny, WHITE, (rect.x + 14, rect.y + 42))
    for i, entry in enumerate(top):
        line = f"{i + 1}. {entry['name']}  -  {entry['score']}"
        draw_text_shadow(surface, line, font_tiny, WHITE, (rect.x + 14, rect.y + 42 + i * 22))


STATE_START, STATE_PLAYING, STATE_GAMEOVER = "start", "playing", "gameover"

FILL_STEP = 150  # score per level / per fill cycle


def reset_game():
    difficulty = DIFFICULTIES[selected_difficulty_index]
    return {
        "bucket": Bucket(SKIN_NAMES[selected_skin_index]),
        "stars": [],
        "obstacles": [],
        "powerups": [],
        "score": 0,
        "lives": 3,
        "level": 1,
        "spawn_timer": 0,
        "spawn_interval": 45,
        "obstacle_timer": 0,
        "powerup_timer": 0,
        "active_powerups": {"magnet": 0, "shield": 0, "slow": 0, "double": 0},
        "shield": False,
        "saved": False,
        "difficulty": difficulty,
        "next_extra_life_score": EXTRA_LIFE_STEP,
    }


state = STATE_START
game = reset_game()
particles.clear()

running = True
while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_click = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if state == STATE_START and name_active:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    name_active = False
                elif len(player_name) < 12 and event.unicode.isprintable():
                    player_name += event.unicode

    draw_background()

    
    if state == STATE_START:
        draw_text_shadow(screen, "BUCKET STAR CATCHER", font_big, GOLD, (WIDTH // 2 - 305, 55))
        draw_text_shadow(screen, "Catch stars, dodge bombs, grab power-ups!",
                          font_small, WHITE, (WIDTH // 2 - 205, 115))

        # name input box
        name_box = pygame.Rect(WIDTH // 2 - 130, 150, 260, 40)
        box_hover = name_box.collidepoint(mouse_pos)
        if mouse_click:
            name_active = box_hover

        
        box_bg = pygame.Surface((name_box.width, name_box.height), pygame.SRCALPHA)
        pygame.draw.rect(box_bg, (20, 20, 40, 160), box_bg.get_rect(), border_radius=8)
        screen.blit(box_bg, name_box.topleft)
        pygame.draw.rect(screen, GOLD if name_active else WHITE, name_box, 2, border_radius=8)

        display_name = player_name + ("|" if name_active and (pygame.time.get_ticks() // 400) % 2 == 0 else "")
        name_label = font_small.render(display_name if display_name else "Enter name", True, WHITE)
        screen.blit(name_label, (name_box.x + 10, name_box.y + 8))
        tiny_label = font_tiny.render("Player name", True, (200, 200, 200))
        screen.blit(tiny_label, (name_box.x, name_box.y - 18))

        # skin selector
        skin_label_y = 195
        left_arrow = pygame.Rect(WIDTH // 2 - 130, skin_label_y, 34, 34)
        right_arrow = pygame.Rect(WIDTH // 2 + 96, skin_label_y, 34, 34)
        draw_button(screen, left_arrow, "<", left_arrow.collidepoint(mouse_pos))
        draw_button(screen, right_arrow, ">", right_arrow.collidepoint(mouse_pos))
        skin_name = SKIN_NAMES[selected_skin_index]
        draw_text_shadow(screen, f"Skin: {skin_name}", font_small, WHITE, (WIDTH // 2 - 68, skin_label_y + 6))
        if mouse_click and left_arrow.collidepoint(mouse_pos):
            selected_skin_index = (selected_skin_index - 1) % len(SKIN_NAMES)
        if mouse_click and right_arrow.collidepoint(mouse_pos):
            selected_skin_index = (selected_skin_index + 1) % len(SKIN_NAMES)

        
        preview = Bucket(SKIN_NAMES[selected_skin_index])
        preview.x = WIDTH // 2 - preview.width // 2
        preview.y = 268
        preview.draw(screen)

        
        diff_label_y = 345
        draw_text_shadow(screen, "Difficulty:", font_small, WHITE, (WIDTH // 2 - 150, diff_label_y))
        diff_buttons = []
        bx = WIDTH // 2 - 30
        for i, diff_name in enumerate(DIFFICULTIES):
            drect = pygame.Rect(bx + i * 95, diff_label_y - 4, 85, 34)
            diff_buttons.append(drect)
            selected = (i == selected_difficulty_index)
            base = (60, 150, 90) if diff_name == "Easy" else (190, 150, 30) if diff_name == "Medium" else (150, 60, 60)
            hover_c = (90, 210, 130) if diff_name == "Easy" else (230, 190, 60) if diff_name == "Medium" else (220, 90, 90)
            draw_button(screen, drect, diff_name, selected or drect.collidepoint(mouse_pos),
                        base_color=base, hover_color=hover_c)
            if selected:
                pygame.draw.rect(screen, WHITE, drect, 3, border_radius=14)
            if mouse_click and drect.collidepoint(mouse_pos):
                selected_difficulty_index = i

        btn_rect = pygame.Rect(WIDTH // 2 - 100, 395, 200, 50)
        hover = btn_rect.collidepoint(mouse_pos)
        draw_button(screen, btn_rect, "PLAY", hover)
        if hover and mouse_click:
            name_active = False
            game = reset_game()
            state = STATE_PLAYING

        draw_text_shadow(screen, "Move: <- -> or A / D",
                          font_tiny, (200, 200, 200), (WIDTH // 2 - 90, 455))

        draw_highscore_panel(screen, pygame.Rect(WIDTH // 2 - 150, 478, 300, 117))

    elif state == STATE_PLAYING:
        keys = pygame.key.get_pressed()

        slow_active = game["active_powerups"]["slow"] > 0
        speed_scale = 0.5 if slow_active else 1.0
        magnet_active = game["active_powerups"]["magnet"] > 0
        double_active = game["active_powerups"]["double"] > 0

        for ptype in game["active_powerups"]:
            if game["active_powerups"][ptype] > 0:
                game["active_powerups"][ptype] -= 1

        game["bucket"].update(keys, speed_scale=1.0)
        bucket_rect = game["bucket"].get_rect()
        bucket_center_x = bucket_rect.centerx

        diff = DIFFICULTY_SETTINGS[game["difficulty"]]

    
        game["spawn_timer"] += 1
        if game["spawn_timer"] >= game["spawn_interval"]:
            game["spawn_timer"] = 0
            sm = (1 + (game["level"] - 1) * 0.12) * diff["star_speed"]
            game["stars"].append(FallingStar(sm))

        
        if game["level"] >= diff["obstacle_level"]:
            game["obstacle_timer"] += 1
            obs_interval = max(60, 160 - game["level"] * 8)
            if game["obstacle_timer"] >= obs_interval:
                game["obstacle_timer"] = 0
                sm = (1 + (game["level"] - 1) * 0.1) * diff["star_speed"]
                game["obstacles"].append(Obstacle(sm))

        
        game["powerup_timer"] += 1
        if game["powerup_timer"] >= 420:  
            game["powerup_timer"] = 0
            if random.random() < 0.8:
                game["powerups"].append(PowerUp())

        
        for star in game["stars"][:]:
            star.update(bucket_center_x, magnet_active, speed_scale)
            if bucket_rect.colliderect(star.get_rect()):
                pts = star.points * (2 if double_active else 1)
                game["score"] += pts
                color = star.get_color()
                spawn_burst(star.x, star.y, color)
                game["bucket"].trigger_catch()
                game["stars"].remove(star)
                continue
            if star.off_screen():
                game["stars"].remove(star)
                if game["shield"]:
                    pass
                else:
                    game["lives"] -= 1
                    trigger_shake(5, 8)
                    spawn_burst(star.x, HEIGHT - 20, RED, count=10)
                    if game["lives"] <= 0:
                        state = STATE_GAMEOVER

        
        for obs in game["obstacles"][:]:
            obs.update(speed_scale)
            if bucket_rect.colliderect(obs.get_rect()):
                game["obstacles"].remove(obs)
                spawn_burst(obs.x, obs.y, (255, 120, 40), count=24, speed_range=(3, 8), life=25)
                trigger_shake(10, 14)
                if game["shield"]:
                    game["shield"] = False
                else:
                    game["lives"] -= 1
                    game["bucket"].shrink = 0.7
                    if game["lives"] <= 0:
                        state = STATE_GAMEOVER
                continue
            if obs.off_screen():
                game["obstacles"].remove(obs)

    
        for pu in game["powerups"][:]:
            pu.update(speed_scale)
            if bucket_rect.colliderect(pu.get_rect()):
                game["powerups"].remove(pu)
                spawn_burst(pu.x, pu.y, POWERUP_COLORS[pu.type], count=16)
                if pu.type == "shield":
                    game["shield"] = True
                elif pu.type == "heart":
                    game["lives"] = min(MAX_LIVES, game["lives"] + 1)
                else:
                    game["active_powerups"][pu.type] = POWERUP_DURATION
                continue
            if pu.off_screen():
                game["powerups"].remove(pu)

    
        game["level"] = 1 + game["score"] // FILL_STEP
        game["spawn_interval"] = max(12, 45 - game["level"] * 3 + diff["spawn_bonus"])
        progress_in_level = (game["score"] % FILL_STEP) / FILL_STEP
        game["bucket"].fill_target = progress_in_level

        
        while game["score"] >= game["next_extra_life_score"]:
            if game["lives"] < MAX_LIVES:
                game["lives"] += 1
                spawn_burst(WIDTH - 60, 25, (255, 90, 90), count=14)
            game["next_extra_life_score"] += EXTRA_LIFE_STEP

        for star in game["stars"]:
            star.draw(screen)
        for obs in game["obstacles"]:
            obs.draw(screen)
        for pu in game["powerups"]:
            pu.draw(screen)

        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.life <= 0:
                particles.remove(p)

        game["bucket"].draw(screen)
        if game["shield"]:
            game["bucket"].draw_shield(screen)

        draw_hud(screen, game)

    elif state == STATE_GAMEOVER:
        if not game["saved"]:
            highscores = save_highscore(player_name, game["score"])
            game["saved"] = True

        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.life <= 0:
                particles.remove(p)

        draw_text_shadow(screen, "GAME OVER", font_big, RED, (WIDTH // 2 - 165, 60))
        draw_text_shadow(screen, f"Final Score: {game['score']}",
                          font_med, WHITE, (WIDTH // 2 - 105, 130))
        draw_text_shadow(screen, f"Level Reached: {game['level']}",
                          font_small, GOLD, (WIDTH // 2 - 90, 170))

        btn_rect = pygame.Rect(WIDTH // 2 - 100, 210, 200, 55)
        hover = btn_rect.collidepoint(mouse_pos)
        draw_button(screen, btn_rect, "RETRY", hover)
        if hover and mouse_click:
            game = reset_game()
            state = STATE_PLAYING

        menu_rect = pygame.Rect(WIDTH // 2 - 100, 275, 200, 45)
        menu_hover = menu_rect.collidepoint(mouse_pos)
        draw_button(screen, menu_rect, "MAIN MENU", menu_hover, base_color=(90, 90, 110), hover_color=(130, 130, 160))
        if menu_hover and mouse_click:
            state = STATE_START

        draw_highscore_panel(screen, pygame.Rect(WIDTH // 2 - 150, 335, 300, 150))

    
    offset = get_shake_offset()
    display_surface.fill(BLACK)
    display_surface.blit(screen, offset)
    pygame.display.flip()

pygame.quit()
sys.exit()