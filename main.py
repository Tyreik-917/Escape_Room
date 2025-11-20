import pygame
import pygame_menu
from player import Player
from level import Level

pygame.init()

width, height = 1920, 1080
center_x, center_y = width//2, height//2
win = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
player = Player(width//2, height//2)

def start():
    menu = pygame_menu.Menu(title="Welcome", width=width, height=height, theme=pygame_menu.themes.THEME_DARK)
    menu.add.label("Press Start to play", font_size=24)
    menu.add.button("Start", game)
    menu.add.button("Quit", pygame_menu.events.EXIT)
    menu.mainloop(win)
def unpause():
    global paused
    paused = False
def pause():
    global paused 
    paused = True
    pause_menu = pygame_menu.Menu(title="Paused", width=width, height=height, theme=pygame_menu.themes.THEME_DARK)
    pause_menu.add.label("Press Resume to continue", font_size=24) 
    pause_menu.add.button("Resume", unpause) # Resume button: just stop the menu loop
    pause_menu.add.button("Quit", pygame_menu.events.EXIT) # Quit button: close menu AND quit game loop
    while paused:
        events = pygame.event.get()
        pause_menu.update(events)
        pause_menu.draw(win)
        pygame.display.update()

def end():
    end_menu = pygame_menu.Menu(title="Congratulations!", width=width, height=height, theme=pygame_menu.themes.THEME_DARK)
    end_menu.add.label("You have completed the game!", font_size=32)
    end_menu.add.button("Back to Menu", start)
    end_menu.add.button("Quit", pygame_menu.events.EXIT)
    end_menu.mainloop(win)


def game():
    player = Player(center_x, center_y)
    level = Level(1)
    while True:
        dt = clock.tick(60)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause()
                elif event.key == pygame.K_e:
                   player.try_interact(level.items)
        # Movement
        old = player.handle_input(keys)
        level.collide_player(old, player.rect)

        # Animation
        frame = player.animate()

        # Drawing
        level.draw(win, player.rect)
        win.blit(frame, (player.rect.x, player.rect.y))
        pygame.draw.rect(win, (255, 0, 0), player.rect, 2)
        
        #next level check

        if level.is_finished():
            level = Level(level.level_id + 1)
            #reposition player
            player.rect.center = (center_x, center_y)
        if level.level_id > 4:
            end()
            break
        pygame.display.flip()
start()
