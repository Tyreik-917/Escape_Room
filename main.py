import pygame
import pygame_menu
from player import Player
from level import Level

pygame.init()

width, height = 1920, 1080
win = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
player = Player(width//2, height//2)
level = Level(1)

def pause(win, width, height):
    paused = True
    pause_menu = pygame_menu.Menu(title="Paused", width=width, height=height, theme=pygame_menu.themes.THEME_DARK)
    pause_menu.add.label("Press Resume to continue", font_size=24) 
    pause_menu.add.button("Resume", game) # Resume button: just stop the menu loop
    pause_menu.add.button("Quit", pygame_menu.events.EXIT) # Quit button: close menu AND quit game loop
    while paused:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
        if pause_menu.is_enabled():
            pause_menu.update(events)
            pause_menu.draw(win)
        pygame.display.update()
        if pause_menu.get_current().get_selected_widget() is None:
            paused = False

def game():
    while True:
        dt = clock.tick(60)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause(win, width, height)

        # Movement
        old = player.handle_input(keys)
        level.collide_player(old, player.rect)

        # Interactions
        if keys[pygame.K_e]:
            player.try_interact(level.items)

        # Animation
        frame = player.animate()

        # Drawing
        level.draw(win, player.rect)
        win.blit(frame, (player.rect.x, player.rect.y))
        pygame.draw.rect(win, (255, 0, 0), player.rect, 2)

        pygame.display.flip()
game()