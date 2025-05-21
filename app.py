import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Set up the screen for full screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Infinite Map with Smooth Camera")

# Get the screen size
screen_width, screen_height = pygame.display.get_surface().get_size()

# Load character image
player_image = pygame.image.load("character.png")
player_image = pygame.transform.scale(player_image, (50, 50))
player_rect = player_image.get_rect(center=(screen_width // 2, screen_height // 2))

# Variables for smooth movement
speed = 5  # Adjust speed of movement

# Camera settings
camera = pygame.Rect(0, 0, screen_width, screen_height)
camera_speed = 0.1

# Player XP and level
player_xp = 0
player_level = 1
xp_to_level_up = 100

# Star class
class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(1, 3)
        self.brightness = random.randint(50, 255)

    def draw(self, surface, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        pygame.draw.circle(surface, (self.brightness, self.brightness, self.brightness),
                           (screen_x, screen_y), self.size)

    def twinkle(self):
        self.brightness += random.randint(-5, 5)
        self.brightness = max(50, min(255, self.brightness))


# XP Ball class
class XpBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 25
        self.image = pygame.image.load("xp.png")
        self.image = pygame.transform.scale(self.image, (self.size, self.size))

    def draw(self, surface, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        surface.blit(self.image, (screen_x - self.size // 2, screen_y - self.size // 2))


# Enemy class
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 50
        self.image = pygame.image.load("enemy.png")
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.angle = 0
        self.speed = 2

    def move_towards_player(self, player_rect):
        dx, dy = player_rect.centerx - self.x, player_rect.centery - self.y
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx /= distance
            dy /= distance
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.angle = (self.angle + 5) % 360

    def resolve_collision(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.hypot(dx, dy)
        if distance < self.size:
            overlap = self.size - distance
            if distance > 0:  # Avoid division by zero
                dx /= distance
                dy /= distance
            self.x += dx * overlap / 2
            self.y += dy * overlap / 2
            other.x -= dx * overlap / 2
            other.y -= dy * overlap / 2

    def draw(self, surface, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center=(screen_x, screen_y))
        surface.blit(rotated_image, new_rect.topleft)

    def collides_with_player(self, player_rect):
        return math.hypot(self.x - player_rect.centerx, self.y - player_rect.centery) < self.size


# Create stars, XP balls, and enemies
stars = [Star(random.randint(0, 10000), random.randint(0, 10000)) for _ in range(1500)]
xp_balls = [XpBall(random.randint(0, 10000), random.randint(0, 10000)) for _ in range(200)]
enemies = []


# Spawn an enemy at random edges
def spawn_enemy():
    edge = random.choice(["top", "bottom", "left", "right"])
    if edge == "top":
        x, y = random.randint(0, 10000), -50
    elif edge == "bottom":
        x, y = random.randint(0, 10000), 10050
    elif edge == "left":
        x, y = -50, random.randint(0, 10000)
    elif edge == "right":
        x, y = 10050, random.randint(0, 10000)
    new_enemy = Enemy(x, y)
    enemies.append(new_enemy)


# Move the character towards the mouse position
def move_towards_mouse(player_rect, mouse_pos, speed, camera):
    map_mouse_x = mouse_pos[0] + camera.x
    map_mouse_y = mouse_pos[1] + camera.y
    dx, dy = map_mouse_x - player_rect.centerx, map_mouse_y - player_rect.centery
    distance = math.hypot(dx, dy)
    if distance > 0:
        dx /= distance
        dy /= distance
        player_rect.centerx += dx * speed
        player_rect.centery += dy * speed
    return dx


# Collect XP balls
def collect_xp(player_rect, xp_balls):
    global player_xp, player_level, xp_to_level_up
    collected_xp = []
    magnet_range = 100
    for xp_ball in xp_balls:
        dist = math.hypot(xp_ball.x - player_rect.centerx, xp_ball.y - player_rect.centery)
        if dist < magnet_range:
            direction_x = (player_rect.centerx - xp_ball.x) / dist
            direction_y = (player_rect.centery - xp_ball.y) / dist
            xp_ball.x += direction_x * 2
            xp_ball.y += direction_y * 2
            if dist < 20:
                player_xp += 10
                collected_xp.append(xp_ball)
    for xp_ball in collected_xp:
        xp_balls.remove(xp_ball)
    if player_xp >= xp_to_level_up:
        player_xp -= xp_to_level_up
        player_level += 1
        xp_to_level_up = int(xp_to_level_up * 1.5)


# Game loop
clock = pygame.time.Clock()
enemy_spawn_timer = 0
enemy_spawn_interval = 200

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    mouse_x, mouse_y = pygame.mouse.get_pos()
    move_direction = move_towards_mouse(player_rect, (mouse_x, mouse_y), speed, camera)

    if move_direction > 0:
        player_image_flipped = pygame.transform.flip(player_image, False, False)
    else:
        player_image_flipped = pygame.transform.flip(player_image, True, False)

    target_camera_x = player_rect.centerx - screen_width // 2
    target_camera_y = player_rect.centery - screen_height // 2
    camera.x += (target_camera_x - camera.x) * camera_speed
    camera.y += (target_camera_y - camera.y) * camera_speed

    collect_xp(player_rect, xp_balls)

    enemy_spawn_timer += clock.get_time()
    if enemy_spawn_timer >= enemy_spawn_interval:
        spawn_enemy()
        enemy_spawn_timer = 0

    for enemy in enemies:
        enemy.move_towards_player(player_rect)
        for other in enemies:
            if enemy != other:
                enemy.resolve_collision(other)
        if enemy.collides_with_player(player_rect):
            print("Collision with player!")

    screen.fill((0, 0, 0))
    for star in stars:
        star.twinkle()
        star.draw(screen, camera)
    for xp_ball in xp_balls:
        xp_ball.draw(screen, camera)
    for enemy in enemies:
        enemy.draw(screen, camera)
    screen.blit(player_image_flipped, player_rect.move(-camera.x, -camera.y))

    font = pygame.font.Font(None, 36)
    level_text = font.render(f"Level: {player_level}", True, (255, 255, 255))
    xp_text = font.render(f"XP: {player_xp}/{xp_to_level_up}", True, (255, 255, 255))
    screen.blit(level_text, (10, 10))
    screen.blit(xp_text, (10, 40))
    pygame.draw.rect(screen, (0, 0, 0), (10, 70, 200, 20))
    pygame.draw.rect(screen, (255, 255, 255), (10, 70, int(200 * (player_xp / xp_to_level_up)), 20))
    pygame.draw.rect(screen, (255, 255, 255), (10, 70, 200, 20), 2)
    pygame.display.flip()
    clock.tick(60)
