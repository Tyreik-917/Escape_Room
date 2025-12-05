import pygame
import random
import time
import os
import platform
import ctypes

if platform.system() == "Windows":
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

if platform.system() == "Darwin":
    os.environ["SDL_HINT_VIDEO_HIGHDPI_DISABLED"] = "0"
    os.environ["PYGAME_FORCE_HIGHDPI"] = "1"

class WhackAMole:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = info.current_w, info.current_h

        self.score = 0
        self.game_duration = 15   # seconds
        self.FPS = 60

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        # Custom events
        self.MOLE_POP_EVENT = pygame.USEREVENT + 1

        # Hole coordinates
        self.HOLE_POSITIONS = [
            (750, 700), (950, 700), (1150, 700),
            (750, 600), (950, 600), (1150, 600),
            (750, 800), (950, 800), (1150, 800)
        ]
        self.MOLE_RADIUS = 30

        # Load assets once
        self.hole_img = pygame.image.load("Assets/hole.png").convert_alpha()
        self.mole_img = pygame.image.load("Assets/mole.png").convert_alpha()
        self.bg_img = pygame.image.load("Assets/basement.png").convert_alpha()
        self.bg_img = pygame.transform.scale(self.bg_img, (self.SCREEN_WIDTH*1.5, self.SCREEN_HEIGHT*1.5))

        self.whack_sound = pygame.mixer.Sound("Assets/whack.mp3")
        self.whack_sound.set_volume(0.25)

        self.taunt_sound = pygame.mixer.Sound("Assets/hehe.mp3")
        self.taunt_sound.set_volume(0.25)

        self.font = pygame.font.Font("Assets/PressStart2P-Regular.ttf", 32)

    # ---------------------------------------------------------
    # Mole Sprite Class
    # ---------------------------------------------------------

    class Mole(pygame.sprite.Sprite):
        def __init__(self, x, y, image):
            super().__init__()
            self.original_pos = (x, y)
            self.image = image
            self.rect = self.image.get_rect(center=(x, y))

            self.is_up = False
            self.hide()

        def show(self, duration_ms):
            self.is_up = True
            self.whack_time = pygame.time.get_ticks() + duration_ms
            self.rect.center = self.original_pos

        def hide(self):
            self.is_up = False
            self.rect.center = (-200, -200)

        def update(self):
            if self.is_up and pygame.time.get_ticks() > self.whack_time:
                self.hide()

    # ---------------------------------------------------------
    # MAIN GAME FUNCTION
    # ---------------------------------------------------------

    def run(self):
        screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        clock = pygame.time.Clock()

        # Setup mole objects
        self.moles = pygame.sprite.Group()
        self.mole_list = []

        for x, y in self.HOLE_POSITIONS:
            mole = self.Mole(x, y, self.mole_img)
            self.moles.add(mole)
            self.mole_list.append(mole)

        # Begin mole popping timer
        pygame.time.set_timer(self.MOLE_POP_EVENT, random.randint(800, 1500))

        start_time = time.time()
        game_over = False

        running = True
        while running:
            elapsed = time.time() - start_time
            time_left = max(0, self.game_duration - elapsed)

            # AUTO-END GAME WHEN TIME RUNS OUT
            if time_left <= 0 and not game_over:
                game_over = True
                pygame.time.set_timer(self.MOLE_POP_EVENT, 0)

                pygame.display.flip()
                pygame.time.delay(1500)

                running = False
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return self.score

                if not game_over:

                    # Handle Whack
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                        for mole in self.mole_list:
                            if mole.is_up and mole.rect.collidepoint(pos):
                                self.score += 1
                                self.whack_sound.play()
                                mole.hide()
                                pygame.event.post(pygame.event.Event(self.MOLE_POP_EVENT))
                                break

                    # Handle Mole Spawning
                    if event.type == self.MOLE_POP_EVENT:
                        hidden = [m for m in self.mole_list if not m.is_up]
                        if hidden:
                            mole = random.choice(hidden)
                            self.taunt_sound.play()
                            mole.show(random.randint(500, 1200))
                        pygame.time.set_timer(self.MOLE_POP_EVENT, random.randint(800, 1500))

            if not game_over:
                self.moles.update()

            # DRAWING
            screen.blit(self.bg_img, (0, 0))

            for x, y in self.HOLE_POSITIONS:
                rect = self.hole_img.get_rect(center=(x, y + 20))
                screen.blit(self.hole_img, (rect))

            self.moles.draw(screen)

            score_text = self.font.render(f"Score: {self.score}", True, self.WHITE)
            time_text = self.font.render(f"Time: {int(time_left)}s", True, self.WHITE)

            screen.blit(score_text, (50, 20))
            screen.blit(time_text, (self.SCREEN_WIDTH - time_text.get_width() - 50, 20))

            pygame.display.flip()
            clock.tick(self.FPS)


        return self.score
