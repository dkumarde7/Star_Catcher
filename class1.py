import pygame
import random
import math
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Class 1 - Animated Background")
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
SKY_TOP = (10, 10, 40)
SKY_BOTTOM = (40, 20, 70)

font_small = pygame.font.SysFont("Arial", 22)

#Gradient Sky
def draw_gradient(surface, top_color, bottom_color):
    """Paints a smooth gradient from top_color to bottom_color."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))


class CloudLayer:
    """A row of drifting clouds.several layers at diffrent speeds create a parallax (depth) illusion."""

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
    CloudLayer(0.40, 190, 80, 0.8, 4)
]


def draw_moon(surface):
    mx, my, mr = WIDTH - 90, 90, 42
    glow = pygame.Surface((mr * 5, mr * 5), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 250, 200, 40), (mr * 2, mr * 2), int(mr * 2.2))
    surface.blit(glow, (mx - mr * 2, my - mr * 2))
    pygame.draw.circle(surface, (250, 250, 210), (mx, my), mr)
    pygame.draw.circle(surface, (230, 220, 210), (mx - 12, my - 8), 8)
    pygame.draw.circle(surface, (230, 220, 180), (mx + 10, my + 14), 10)

def draw_mountains(surface):
    layers = [
        ((30, 20, 55), HEIGHT - 40, 60),
        ((40, 30, 70), HEIGHT - 10, 90),
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

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

    draw_background()

    label = font_small.render("Class 1: Animated Background. escape to quit", True, WHITE)        
    screen.blit(label, (20, HEIGHT - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
