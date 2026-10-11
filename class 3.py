

import pygame
import random
import math
import sys
import colorsys


pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Class 3 - Falling Stars & Score")
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
RED = (255, 80, 80)
GOLD = (255, 215, 0)
SKY_TOP = (10, 10, 40)
SKY_BOTTOM = (40, 20, 70)

font_med = pygame.font.SysFont("arial", 30, bold=True)
font_small = pygame.font.SysFont("arial", 22)
font_big = pygame.font.SysFont("arial", 60, bold=True)


def draw_text_shadow(surface, text, font, color, pos, shadow_color=(0, 0, 0)):
    x, y = pos
    shadow = font.render(text, True, shadow_color)
    surface.blit(shadow, (x + 3, y + 3))
    main = font.render(text, True, color)
    surface.blit(main, (x, y))


def draw_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))


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


BUCKET_SKINS = {
    "Wood": {"top": (200, 130, 70), "bottom": (120, 70, 35), "rim": (215, 160, 95),
             "outline": (80, 48, 22), "handle": (150, 100, 55)},
}


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
        surface.blit(body_surf, body_rect.topleft)

        pygame.draw.polygon(surface, colors["outline"], body_points, 3)

        rim_rect = pygame.Rect(left_x + wobble, top_y - 9, w, 18)
        pygame.draw.ellipse(surface, colors["rim"], rim_rect)
        pygame.draw.ellipse(surface, colors["outline"], rim_rect, 3)

        handle_rect = pygame.Rect(cx - w * 0.32 + tilt, top_y - 30, w * 0.64, 34)
        pygame.draw.arc(surface, colors["outline"], handle_rect, math.radians(15), math.radians(165), 4)
        pygame.draw.arc(surface, colors["handle"], handle_rect, math.radians(15), math.radians(165), 2)


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
    "silver": {"color": (210, 215, 230), "points": 5, "speed_mult": 0.9, "weight": 40},
    "normal": {"color": (255, 240, 150), "points": 10, "speed_mult": 1.0, "weight": 35},
    "gold":   {"color": (255, 215, 0),   "points": 25, "speed_mult": 1.1, "weight": 18},
    "rainbow": {"color": None,           "points": 50, "speed_mult": 1.25, "weight": 7},
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

    def get_color(self):
        if self.type == "rainbow":
            hue = (pygame.time.get_ticks() * 0.0006) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.75, 1.0)
            return (int(r * 255), int(g * 255), int(b * 255))
        return self.base_color

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        draw_star_shape(surface, (self.x, self.y), self.size, self.get_color())

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


def reset_game():
    return {
        "bucket": Bucket("Wood"),
        "stars": [],
        "score": 0,
        "lives": 3,
        "spawn_timer": 0,
        "spawn_interval": 45,
        "game_over": False,
    }


game = reset_game()

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r and game["game_over"]:
                game = reset_game()
                particles.clear()

    draw_background()

    if not game["game_over"]:
        keys = pygame.key.get_pressed()
        game["bucket"].update(keys)
        bucket_rect = game["bucket"].get_rect()

        # spawn a new star every `spawn_interval` frames
        game["spawn_timer"] += 1
        if game["spawn_timer"] >= game["spawn_interval"]:
            game["spawn_timer"] = 0
            game["stars"].append(FallingStar())

        # update + collide stars
        for star in game["stars"][:]:
            star.update()
            if bucket_rect.colliderect(star.get_rect()):
                game["score"] += star.points
                spawn_burst(star.x, star.y, star.get_color())
                game["bucket"].trigger_catch()
                game["stars"].remove(star)
                continue
            if star.off_screen():
                game["stars"].remove(star)
                game["lives"] -= 1
                spawn_burst(star.x, HEIGHT - 20, RED, count=10)
                if game["lives"] <= 0:
                    game["game_over"] = True

        for star in game["stars"]:
            star.draw(screen)

    for p in particles[:]:
        p.update()
        p.draw(screen)
        if p.life <= 0:
            particles.remove(p)

    game["bucket"].draw(screen)

    draw_text_shadow(screen, f"Score: {game['score']}", font_med, WHITE, (20, 15))
    for i in range(game["lives"]):
        hx = WIDTH - 40 - i * 35
        pygame.draw.circle(screen, RED, (hx, 25), 10)
        pygame.draw.circle(screen, RED, (hx + 12, 25), 10)
        pygame.draw.polygon(screen, RED, [(hx - 10, 30), (hx + 22, 30), (hx + 6, 50)])

    if game["game_over"]:
        draw_text_shadow(screen, "GAME OVER", font_big, RED, (WIDTH // 2 - 165, HEIGHT // 2 - 60))
        draw_text_shadow(screen, "Press R to restart", font_small, WHITE, (WIDTH // 2 - 90, HEIGHT // 2 + 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
