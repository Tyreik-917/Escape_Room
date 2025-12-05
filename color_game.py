import pygame
import random
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

WHITE = (255,255,255)
BLACK = (0,0,0)
FONT = pygame.font.SysFont("Assets/PressStart2P-Regular.ttf", 32)
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

def draw_text(surface, text, pos, color=WHITE, font=FONT):
    surf = font.render(text, True, color)
    surface.blit(surf, pos)

class ColorMemoryGame:
    def __init__(self, screen):
        self.screen = screen
        self.colors = [(255,0,0),(0,255,0),(0,0,255),(128,128,128)]
        self.color_names = ["Red","Green","Blue","Gray"]
        num_boxes = 4
        box_width = 120
        spacing = 60  # space between boxes
        total_width = num_boxes * box_width + (num_boxes - 1) * spacing
        start_x = WIDTH // 2 - total_width // 2
        y_pos = 490
        self.boxes = [pygame.Rect(start_x + i * (box_width + spacing), y_pos, box_width, box_width) for i in range(num_boxes)]

    def play_sequence(self, sequence):
        for color_index in sequence:
            self.screen.fill(BLACK)
            for i, box in enumerate(self.boxes):
                clr = self.colors[i] if i==color_index else (50,50,50)
                pygame.draw.rect(self.screen, clr, box)
                draw_text(self.screen, self.color_names[i], (box.x, box.y-30))
            pygame.display.flip()
            pygame.time.wait(700)
        pygame.time.wait(500)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return self.game_loop()
                    if event.key == pygame.K_ESCAPE:
                        return False
            self.screen.fill(BLACK)
            draw_text(self.screen, "COLOR MEMORY GAME", (740,300))
            draw_text(self.screen, "Press SPACE to start", (740,350))
            draw_text(self.screen, "Press Esc to exit", (740,400))
            draw_text(self.screen, "Use your mouse to play", (740,450))
            draw_text(self.screen, "But wait until the colors stop flashing to input your answer", (740,500))
            pygame.display.flip()

    def game_loop(self):
        sequence = []
        prev = -1
        for _ in range(4):
            c = random.randint(0,3)
            while c==prev:
                c=random.randint(0,3)
            sequence.append(c)
            prev = c
        index = 0
        clicked = None
        self.play_sequence(sequence)
        pygame.event.clear()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx,my = event.pos
                    for i, box in enumerate(self.boxes):
                        if box.collidepoint(mx,my):
                            clicked=i
                            ding_sound = pygame.mixer.Sound("Assets/ding.mp3")
                            ding_sound.play()
                            if i==sequence[index]:
                                index+=1
                                if index==len(sequence): return True
                            else: return False
            self.screen.fill(BLACK)
            for i, box in enumerate(self.boxes):
                clr=self.colors[i]
                if clicked==i:
                    clr=(min(clr[0]+70,255), min(clr[1]+70,255), min(clr[2]+70,255))
                pygame.draw.rect(self.screen, clr, box)
                draw_text(self.screen, self.color_names[i], (box.x, box.y-30))
            pygame.display.flip()
