import pygame
import pygame_menu
import time
from player import Player
from level import Level

pygame.init()

width, height = 1920, 1080
center_x, center_y = width//2, height//2
win = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
player = Player(width//2, height//2)

ui_font = pygame.font.Font("PressStart2P-Regular.ttf", 32)  # adjust size if needed
current_message = ""
message_timer = 0
message_queue = []
def show_message(text, duration=2, size=32, queue=False):
    global current_message, message_timer, ui_font, message_queue
    if queue and current_message:
        message_queue.append((text, duration, size))
        return
    ui_font = pygame.font.Font("PressStart2P-Regular.ttf", size)
    current_message = text
    message_timer = time.time() + duration

def start():
    pygame.mixer.music.load("start_menu_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    background_image = pygame_menu.baseimage.BaseImage("start_background.png")
    my_theme = pygame_menu.Theme(
        title=False,
        background_color=background_image,
        widget_font = pygame.font.Font("PressStart2P-Regular.ttf", 32),
        widget_font_size = 40,
        widget_font_color = (255, 255, 255),
        widget_padding = 10,
        selection_color = (255, 255, 0),
        widget_alignment = pygame_menu.locals.ALIGN_CENTER
    )
    my_theme.widget_selection_effect = pygame_menu.widgets.HighlightSelection(
        border_width=5,   # thicker border
        margin_x=100,       # wider box
        margin_y=70        # taller box
    )
    menu = pygame_menu.Menu("Welcome", width, height, theme=my_theme)
    img = menu.add.image("start_select.png")
    start = menu.add.button("         ", game)
    quit  = menu.add.button("         ", pygame_menu.events.EXIT)
    img.translate(0, 0)
    start.translate(-9, -289.5)
    quit.translate(-9, -215)
    menu.mainloop(win)


def unpause():
    global paused
    paused = False
def pause():
    global paused 
    paused = True
    pygame.mixer.music.load("pause_menu_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    screen_surface = win.copy()
    my_theme = pygame_menu.Theme(
        title=False,
        background_color=(50, 50, 50, 200),   # transparentish
        widget_alignment=pygame_menu.locals.ALIGN_CENTER,
        widget_font=pygame.font.Font("PressStart2P-Regular.ttf", 32),
        widget_font_size=40,
        widget_font_color=(255, 255, 255),
        selection_color=(255, 255, 0),
    )
    my_theme.widget_selection_effect = pygame_menu.widgets.HighlightSelection(
        border_width=5,   # thicker border
        margin_x=105,       # wider box
        margin_y=75        # taller box
    )
    pause_menu = pygame_menu.Menu(title="Paused", width=width, height=height, theme=my_theme)
    img = pause_menu.add.image("pause_select.png")
    resume = pause_menu.add.button("         ", unpause)
    quit  = pause_menu.add.button("         ", start)
    img.translate(0, 0)
    resume.translate(-9, -277.5)
    quit.translate(-9, -190) 
    while paused:
        win.blit(screen_surface, (0, 0))
        events = pygame.event.get()
        pause_menu.update(events)
        pause_menu.draw(win)
        pygame.display.update()
    pygame.mixer.music.stop()
def end():
    frames = [
        "end_1.png", "end_2.png", "end_3.png", "end_4.png", "end_5.png",
        "end_6.png", "end_7.png", "end_8.png", "end_9.png", "end_10.png",
        "end_11.png", "end_12.png", "end_13.png", "end_14.png", "end_15.png"
    ]
    for frame in frames:
        img = pygame.image.load(frame).convert_alpha()
        img = pygame.transform.scale(img,(1920, 1150))
        win.blit(img, (0, 0))
        pygame.display.flip()
        if frame == frames[2]:
            pygame.time.delay(800)
        elif frame == frames[11] or frame == frames[12] or frame == frames[13] or frame == frames[14]:
            time.sleep(.0001)
        else:
            pygame.time.delay(300)
        if frame == frames[0]:
            pygame.mixer.music.load("end_menu_music.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        if frame == frames[10]:
            pygame.time.delay(1000)   
    pygame.time.delay(3000)
    screen_surface = win.copy()
    pygame.image.save(screen_surface, "temp_pause_bg.png")
    background_image = pygame_menu.baseimage.BaseImage(image_path="temp_pause_bg.png")
    my_theme = pygame_menu.Theme(
        title=False,
        background_color=background_image,
        widget_alignment=pygame_menu.locals.ALIGN_CENTER,
        widget_font=pygame.font.Font("PressStart2P-Regular.ttf", 32),
        widget_font_size=40,
        widget_font_color=(255, 255, 255),
        selection_color=(255, 255, 0),
    )
    my_theme.widget_selection_effect = pygame_menu.widgets.HighlightSelection(
        border_width=5,   # thicker border
        margin_x=105,       # wider box
        margin_y=75        # taller box
    )
    end_menu = pygame_menu.Menu("Thank you", width, height, theme=my_theme)
    img = end_menu.add.image("end_select.png")
    menu= end_menu.add.button("         ", start)
    quit  = end_menu.add.button("         ", pygame_menu.events.EXIT)
    img.translate(0, 0)
    menu.translate(-9, -277.5)
    quit.translate(-9, -190) 
    end_menu.draw(win)
    end_menu.mainloop(win)


def game():
    global current_message, message_timer, message_queue, ui_font
    pygame.mixer.music.stop()
    player = Player(center_x, center_y)
    level = Level(1, show_message)
    
    while True:
        dt = clock.tick(60)
        level.update_interactable(player)
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
        if level.level_id == 1:
            top_limit = 150
        elif level.level_id == 2:
            top_limit = 250
        elif level.level_id == 3:
            top_limit = 150
        elif level.level_id == 4:
            top_limit = 150
        old, dx, dy = player.handle_input(keys, top_limit=top_limit)
        level.collide_player(old, player.rect, dx, dy)
        # Animation
        frame = player.animate()
        level.draw(win, player.rect)
        win.blit(frame, (player.rect.x, player.rect.y))
        
        #next level check
        if level.is_finished():
            level = Level(level.level_id + 1, show_message)
            #reposition player
            player.rect.center = (center_x, center_y)
        if level.level_id > 4:
            end()
            break

        # Display message
        if current_message and time.time() < message_timer:
            box_rect = pygame.Rect(0, height - 120, width, 120)
            pygame.draw.rect(win, (255, 255, 255), box_rect)
            pygame.draw.rect(win, (0, 0, 0), box_rect, 4)
            text_surface = ui_font.render(current_message, True, (0, 0, 0))
            win.blit(text_surface, (40, height - 90))
        if current_message and time.time() >= message_timer:
            if message_queue:
                text, duration, size = message_queue.pop(0)
                ui_font = pygame.font.Font("PressStart2P-Regular.ttf", size)
                current_message = text
                message_timer = time.time() + duration
            else:
                current_message = ""
        pygame.display.flip()
start()
