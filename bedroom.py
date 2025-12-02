import pygame
import sys
import random
from pathlib import Path

# Configuration
WIDTH, HEIGHT = 1000, 600
FPS = 60
PLAYER_SPEED = 180  # pixels per second
PLAYER_RADIUS = 14

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
WALL = (200, 220, 235)

# Initialize pygame and mixer
pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("Warning: pygame.mixer couldn't initialize:", e)

FONT = pygame.font.SysFont("arial", 18)
BIGFONT = pygame.font.SysFont("arial", 28)
CLOCK = pygame.time.Clock()

def draw_text(surface, text, pos, color=BLACK, font=FONT):
    surf = font.render(text, True, color)
    surface.blit(surf, pos)

# Glow helper function
def draw_glow(surface, rect, color=(255, 255, 100, 160), padding=6):
    glow_rect = rect.inflate(padding*2, padding*2)
    glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, color, glow_surf.get_rect(), border_radius=12)
    surface.blit(glow_surf, glow_rect.topleft)

# Player Class
class Player:
    def __init__(self, x, y, sprite_size=64):
        self.sprite_size = sprite_size
        self.rect = pygame.Rect(0, 0, sprite_size, sprite_size)
        self.rect.center = (x, y)
        self.speed = PLAYER_SPEED
        self.frames = []
        self.has_sprites = False

        try:
            for name in ("idle.png", "walk_1.png", "walk_2.png"):
                img = pygame.image.load(name).convert_alpha()
                img = pygame.transform.smoothscale(img, (sprite_size, sprite_size))
                self.frames.append(img)
            if self.frames:
                self.has_sprites = True
        except:
            print("Player sprites not found. Using fallback.")
            self.has_sprites = False

        self.frame_index = 0.0
        self.animation_speed = 8.0
        self.moving = False
        self.facing_right = True
        self.last_interact = 0.0
        self.interact_cooldown = 0.4
        self.inventory = []

    def handle_input_and_move(self, keys, dt, boundaries):
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if dx != 0 and dy != 0:
            diag = 0.70710678
            dx *= diag
            dy *= diag

        self.moving = dx != 0 or dy != 0
        if dx < 0: self.facing_right = False
        elif dx > 0: self.facing_right = True

        # Horizontal movement and collision
        self.rect.x += int(dx * self.speed * dt)
        for o in boundaries:
            if self.rect.colliderect(o):
                if dx > 0: self.rect.right = o.left
                elif dx < 0: self.rect.left = o.right

        # Vertical movement and collision
        self.rect.y += int(dy * self.speed * dt)
        for o in boundaries:
            if self.rect.colliderect(o):
                if dy > 0: self.rect.bottom = o.top
                elif dy < 0: self.rect.top = o.bottom

        # Animation
        if self.has_sprites:
            if self.moving:
                self.frame_index += self.animation_speed * dt
                if self.frame_index >= len(self.frames):
                    self.frame_index = 0
            else:
                self.frame_index = 0

    def get_draw_surface(self):
        if self.has_sprites:
            img = self.frames[int(self.frame_index)]
            if not self.facing_right:
                img = pygame.transform.flip(img, True, False)
            return img
        else:
            return None

    def center_pos(self):
        return self.rect.center

# Item Class
class Item:
    def __init__(self, name, rect, color=(240, 220, 100)):
        self.name = name
        self.rect = pygame.Rect(rect)
        self.color = color
        self.picked = True

    def draw(self, surf):
        if not self.picked:
            pygame.draw.rect(surf, self.color, self.rect)
            draw_text(surf, self.name, (self.rect.x, self.rect.y - 18))

    def is_near(self, player_rect, margin=24):
        return player_rect.colliderect(self.rect.inflate(margin, margin))

# Door Class
class Door:
    def __init__(self, rect, locked=True):
        self.rect = pygame.Rect(rect)
        self.locked = locked
        self.open = False
        self.open_progress = 0 # 0 = closed, 1 = fully open

    def draw(self, surf, door_img=None):
        if door_img:
            if self.open:
                scale = max(0.05, 1.0 - self.open_progress)
                w = int(self.rect.width * scale)
                img = pygame.transform.smoothscale(door_img, (w, self.rect.height))
            else:
                img = door_img
            surf.blit(img, self.rect.topleft)
        else:
            pygame.draw.rect(surf, (90, 50, 18), self.rect)
        label = "Locked (E)" if self.locked else "Unlocked (E)"
        draw_text(surf, label, (self.rect.x, self.rect.y - 26))

# Color Memory Minigame
class ColorMemoryGame:
    def __init__(self, screen):
        self.screen = screen
        self.colors = [(255, 0, 0),(0, 255, 0),(0, 0, 255),(128, 128, 128)]
        self.color_names = ["Red", "Green", "Blue", "Gray"]
        self.boxes = [pygame.Rect(200 + i*150, 300, 100, 100) for i in range(4)]

        # Load ding sound
        try:
            if Path("ding.mp3").exists():
                self.ding_sound = pygame.mixer.Sound("ding.mp3")
            else:
                self.ding_sound = None
        except Exception as e:
            print("Warning: could not load ding.mp3:", e)
            self.ding_sound = None

    def play_sequence(self, sequence):
        for color in sequence:
            self.screen.fill(BLACK)
            for i, box in enumerate(self.boxes):
                clr = self.colors[i] if i == color else (60, 60, 60)
                pygame.draw.rect(self.screen, clr, box)
                draw_text(self.screen, self.color_names[i], (box.x+8, box.y-24), WHITE)
            pygame.display.flip()
            pygame.time.wait(800)
        pygame.time.wait(800)

    def run(self):
        # Start screen
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: return False
                    if event.key == pygame.K_SPACE: waiting = False

            self.screen.fill(BLACK)
            draw_text(self.screen, "COLOR MEMORY GAME", (400, 200), WHITE)
            draw_text(self.screen, "Press SPACE to begin", (405, 300), WHITE)
            draw_text(self.screen, "Press Q to quit", (440, 350), WHITE)
            pygame.display.flip()

        # Game sequence loop
        while True:
            sequence = []
            prev = -1
            for _ in range(4):
                c = random.randint(0, 3)
                while c == prev:
                    c = random.randint(0, 3)
                sequence.append(c)
                prev = c
            idx = 0
            self.play_sequence(sequence)

            playing = True
            clicked_color = None      # the last clicked color (for persistent lighting)
            last_clicked_input = None # prevents counting the same click twice in a row

            while playing:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                        return False

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = event.pos
                        for i, box in enumerate(self.boxes):
                            if box.collidepoint(mx, my):
                                # ignore if this is the same immediate repeated click
                                if last_clicked_input == i:
                                    # do nothing; ignore duplicate immediate click
                                    break

                                # set clicked color so it stays lit
                                clicked_color = i
                                last_clicked_input = i

                                # play ding sound when clicked
                                if self.ding_sound:
                                    try:
                                        self.ding_sound.play()
                                    except Exception:
                                        pass

                                # check correctness of input
                                if i == sequence[idx]:
                                    idx += 1
                                    # if sequence complete, player wins this round
                                    if idx == len(sequence):
                                        return True
                                else:
                                    playing = False
                                break

                    # reset last_clicked_input on mouseup so repeated presses require real releasing
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        last_clicked_input = None

                # Hover Highlighting
                mx, my = pygame.mouse.get_pos()
                self.screen.fill(BLACK)
                for i, box in enumerate(self.boxes):
                    clr = self.colors[i]
                    # Hover detection
                    hovering = box.collidepoint(mx, my)

                    if clicked_color == i:
                        bright = tuple(min(255, c + 80) for c in clr)
                        pygame.draw.rect(self.screen, bright, box)
                        draw_glow(self.screen, box, (255, 255, 200, 180), 10)
                    elif hovering:
                        bright = tuple(min(255, c + 60) for c in clr)
                        pygame.draw.rect(self.screen, bright, box)
                        draw_glow(self.screen, box, (255, 255, 180, 160), 10)
                    else:
                        pygame.draw.rect(self.screen, clr, box)

                    draw_text(self.screen, self.color_names[i], (box.x + 10, box.y - 26), WHITE)

                pygame.display.flip()

                # Incorrect - show message
                if not playing:
                    self.screen.fill(BLACK)
                    draw_text(self.screen, "WRONG! Try Again.", (380, 200), WHITE)
                    pygame.display.flip()
                    pygame.time.wait(1000)
                    break

# Escape Room Background
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Escape Room: Bedroom")
        self.clock = CLOCK
        self.bg = pygame.image.load("bedroom.png").convert() # Background image
        self.bg = pygame.transform.smoothscale(self.bg, (WIDTH, HEIGHT)) # Background Image Size
        self.door_img = pygame.image.load("door.png").convert_alpha() # Door Image
        self.door_img = pygame.transform.smoothscale(self.door_img, (92, 192)) # Door Image Size
        self.door = Door((450, 0, 92, 192), locked=True) # Door Position
        self.dresser_img = pygame.image.load("dresser.png").convert_alpha() # Dresser Image
        self.dresser_img = pygame.transform.smoothscale(self.dresser_img, (100, 150)) # Dresser Image Size
        self.dresser_rect = pygame.Rect(250, 94, 100, 150) # Dresser Position
        self.player = Player(500, 350) # Player Start Position
        self.message = "Press E near the dresser to play the memory game."
        self.show_inventory = False
        self.win = False

        self.key = Item("Key", (110, 10, 20, 12))
        self.key.picked = True
        self.items = [self.key]

        self.dresser_used = False

        self.boundaries = [
            pygame.Rect(0, 0, WIDTH, 6), pygame.Rect(0, HEIGHT - 6, WIDTH, 6),
            pygame.Rect(0, 0, 6, HEIGHT), pygame.Rect(WIDTH - 6, 0, 6, HEIGHT)
        ]

    def reset(self):
        self.__init__()

    def handle_events(self, dt):
        keys = pygame.key.get_pressed()
        self.player.handle_input_and_move(keys, dt, self.boundaries)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e: self.try_interact()
                if event.key == pygame.K_i: self.show_inventory = not self.show_inventory
                if event.key == pygame.K_r: self.reset()

    def try_interact(self): # Dresser interaction
        if not self.dresser_used and self.player.rect.colliderect(self.dresser_rect.inflate(20, 20)):
            mem = ColorMemoryGame(self.screen)
            won = mem.run()
            self.dresser_used = True

            if won:
                if "Key" not in self.player.inventory:
                    self.player.inventory.append("Key")
                self.message = "You won the puzzle and received a Key!"
            else:
                self.message = "You exited the puzzle."
            return

        # Door
        if self.player.rect.colliderect(self.door.rect.inflate(12, 12)):
            if self.door.locked:
                if "Key" in self.player.inventory:
                    self.door.locked = False
                    self.door.open = True
                    self.message = "You used the Key. Door unlocked! Press E to escape."
                else:
                    self.message = "The door is locked. You need a Key."
            else:
                self.win = True
                self.message = "You escaped! Press R to restart."

    def update(self, dt):
        if self.door.open and self.door.open_progress < 1.0:
            self.door.open_progress += dt # animate door opening

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        # Dresser glows if player is near
        if self.player.rect.colliderect(self.dresser_rect.inflate(40, 40)):
            draw_glow(self.screen, self.dresser_rect)
        # Draw dresser
        self.screen.blit(self.dresser_img, self.dresser_rect.topleft)
        # Items
        for item in self.items:
            if not item.picked:
                item.draw(self.screen)
        # Door
        self.door.draw(self.screen, self.door_img)
        # Player
        surf = self.player.get_draw_surface()
        cx, cy = self.player.center_pos()

        if surf:
            self.screen.blit(surf, surf.get_rect(center=(cx, cy)))
        else:
            pygame.draw.circle(self.screen, (30, 90, 200), (cx, cy), PLAYER_RADIUS)

        # Draw inventory status
        pygame.draw.rect(self.screen, (240, 240, 240), (8, HEIGHT - 52, WIDTH - 16, 44))
        draw_text(self.screen, self.message, (16, HEIGHT - 44))
        draw_text(self.screen, "Inventory: " + (", ".join(self.player.inventory) if self.player.inventory else "(empty)"), (16, 8))

        # Draw Win screen overlay
        if self.win:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            draw_text(self.screen, "YOU ESCAPED!", (WIDTH // 2 - 80, HEIGHT // 2 - 40), WHITE, BIGFONT)

    def run(self):
        while True:
            dt = self.clock.tick(FPS)/1000.0
            self.handle_events(dt)
            self.update(dt)
            self.draw()
            pygame.display.flip()

if __name__ == "__main__":
    Game().run()
