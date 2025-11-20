import pygame
import time
from item import Item, Crate, Table, Statue
width, height = 1920, 1080
center_x, center_y = width//2, height//2
class Player:
    def __init__(self, x, y, sprite_size=128):
        self.rect = pygame.Rect(0, 0, sprite_size, sprite_size)
        self.rect.center = (x, y)
        self.speed = 5

        # animation
        self.frames = [
            pygame.image.load("idle.png"),
            pygame.image.load("walk_1.png"),
            pygame.image.load("walk_2.png")
        ]
        self.frames = [pygame.transform.scale(f, (sprite_size, sprite_size)) for f in self.frames]

        self.frame_index = 0
        self.animation_speed = 0.15
        self.moving = False
        self.facing_right = True

        # interaction
        self.last_interact = 0
        self.interact_cooldown = 0.5

        # sound
        self.footstep = pygame.mixer.Sound("footstep.mp3")
        self.footstep.set_volume(0.3)

    def handle_input(self, keys):
        old = self.rect.copy()
        self.moving = False

        if keys[pygame.K_w]:
            self.rect.y -= self.speed
            self.moving = True
        if keys[pygame.K_s]:
            self.rect.y += self.speed
            self.moving = True
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.moving = True
            self.facing_right = False
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.moving = True
            self.facing_right = True
    
        top_limit = 200
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > width:
            self.rect.right = width
        if self.rect.top < top_limit:
            self.rect.top = top_limit
        if self.rect.bottom > height:
            self.rect.bottom = height
            

        return old  # return previous position for collision revert

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
            if item.is_active and item.is_near(self.rect) and item.interactable:
                item.interact()
                self.last_interact = now
                break
