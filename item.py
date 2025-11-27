# item.py
import pygame
import time

screen_w = 1920
screen_h = 1080
half_w = screen_w // 2
half_h = screen_h // 2

class Item:
    """Base class for all items."""

    def __init__(self, name, image_path, pos, size=(1,1), collision=True, interactable=True):
        self.name = name
        self.image = pygame.image.load(image_path)
        world_x, world_y = pos
        screen_x = world_x + half_w
        screen_y = half_h - world_y
        self.rect = self.image.get_rect(center=(screen_x, screen_y)) #centers image starting pos
        self.collision = collision
        self.interactable = interactable
        self.near_start = None
        self.glow = False

        resize = (self.rect.width*size[0], self.rect.height*size[1])
        if resize != None:
            self.image = pygame.transform.scale(self.image, resize)
        self.rect = self.image.get_rect(center=(screen_x, screen_y))
        world_x = max(-half_w + self.rect.width//2, min(world_x, half_w - self.rect.width//2))
        world_y = max(-half_h + self.rect.height//2, min(world_y, half_h - self.rect.height//2))
        self.rect.center = (world_x + half_w, half_h - world_y)

        x = max(self.rect.width, 150)
        y = max(self.rect.height, 150)
        self.interact_radius = (x,y)
        self.glow_surface = self.create_glow_surface()
        self.is_active = True  # Used for disabling after interaction
        self.is_finished = False

    def create_glow_surface(self):
        glow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        glow.fill((255, 255, 255, 100))
        return glow

    def is_near(self, player_rect):
        dx = abs(self.rect.centerx - player_rect.centerx)
        dy = abs(self.rect.centery - player_rect.centery)
        distance = (dx,dy)
        return distance[0] < self.interact_radius[0] and distance[1] < self.interact_radius[1]

    def set_message_callback(self, callback):
        self.show_message = callback

    def draw(self, surface, player_rect, show_hitbox=False):
        if not self.is_active:
            return
        surface.blit(self.image, self.rect.topleft)
        if self.is_near(player_rect) and self.interactable and self.glow:
            surface.blit(self.glow_surface, self.rect.topleft)
            if self.near_start is None:
                self.near_start = time.time()
            if time.time() - self.near_start >= 10:
                self.show_message(f"You can interact with {self.name} (press E)")
        else:
            self.near_start = None
        if show_hitbox:
            pygame.draw.rect(surface, (0, 255, 0), self.rect, 2)

    def collides_with(self, other_rect):
        return self.is_active and self.rect.colliderect(other_rect)


#Specialized item types
# level 1
class Statue_m(Item):
    def interact(self):
        wine = globals().get('wine', False)
        if wine == False:
            self.show_message(f"The statue seems to be missing something...", 3)
        elif wine == True:
            self.show_message(f"You gave the wine to the statue. It seems satisfied.", 3)
        self.is_finished = True

class Statue_f(Item):
    def interact(self):
        global wine
        wine = True
        print("statue")
        self.is_finished = True

class Picture(Item):
    def interact(self):
        print("picture")
        self.is_finished = True


# level 2


# level 3


# level 4


#same for each level
class Door(Item):
    def interact(self):
        self.is_finished = True
        
