import pygame
import time
import ctypes
ctypes.windll.user32.SetProcessDPIAware()  # for Windows DPI scaling issues
pygame.init()
width, height = 1920, 1080
center_x, center_y = width//2, height//2
class Player:
    def __init__(self, x, y, sprite_size=128):
        sprite_size = height//8
        self.rect = pygame.Rect(0, 0, sprite_size, sprite_size)
        self.rect.center = (x, y)
        self.speed = height//108

        # animation
        self.frames = [
            pygame.image.load("Assets/idle.png"),
            pygame.image.load("Assets/walk_1.png"),
            pygame.image.load("Assets/walk_2.png")
        ]
        self.frames = [pygame.transform.scale(f, (sprite_size, sprite_size)) for f in self.frames]

        self.frame_index = 0
        self.animation_speed = 3/self.speed
        self.moving = False
        self.facing_right = True

        # interaction
        self.last_interact = 0
        self.interact_cooldown = 0.5

        # sound
        self.footstep = pygame.mixer.Sound("Assets/footstep.mp3")
        self.footstep.set_volume(0.3)

    def handle_input(self, keys, top_limit=200):
        old = self.rect.copy()
        self.moving = False

        dx = 0
        dy = 0

        if keys[pygame.K_w]:
            dy -= self.speed
            self.moving = True
        if keys[pygame.K_s]:
            dy += self.speed
            self.moving = True
        if keys[pygame.K_a]:
            dx -= self.speed
            self.moving = True
            self.facing_right = False
        if keys[pygame.K_d]:
            dx += self.speed
            self.moving = True
            self.facing_right = True

        # Apply movement
        self.rect.x += dx
        self.rect.y += dy

        # Screen bounds
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > width: self.rect.right = width
        if self.rect.top < top_limit: self.rect.top = top_limit
        if self.rect.bottom > height: self.rect.bottom = height

        return old, dx, dy  # return previous position AND movement deltas

    def animate(self):
        if self.moving:
            self.frame_index += self.animation_speed
            if not pygame.mixer.get_busy():
                self.footstep.play()
        else:
            self.frame_index = 0

        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        frame = self.frames[int(self.frame_index)]

        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        return frame

    def try_interact(self, items):
        now = time.time()
        if now - self.last_interact < self.interact_cooldown:
            return

        for item in items:
            if item.is_active and item.is_near(self.rect) and item.interactable and item.reinteractable:
                if getattr(item, "can_interact_now", False):
                    pygame.mixer.stop()
                    item.interact()
                    self.last_interact = now
                    break