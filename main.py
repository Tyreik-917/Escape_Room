# -----------------------------
# Imports & Initialization
# -----------------------------
import pygame
import pygame_menu
import time
from player import Player         # Custom Player class
from level import Level           # Custom Level system

pygame.init()

# -----------------------------
# Window / Display Setup
# -----------------------------
info = pygame.display.Info()
width, height = info.current_w, info.current_h
#width, height = 1920, 1080  
center_x, center_y = width // 2, height // 2
win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) #Window 
clock = pygame.time.Clock()

# Create the player at the center of the screen
#player = Player(width // 2, height // 2)     Put back if needed

# -----------------------------
# UI Message System (bottom textbox)
# -----------------------------
ui_font = pygame.font.Font("Main/PressStart2P-Regular.ttf", 32)
current_message = ""          # Text currently being displayed
message_timer = 0             # When the message should disappear
message_queue = []            # Queue for stacking multiple messages


def show_message(text, duration=2, size=32, queue=False):
    """
    Displays text at the bottom of the screen.
    If queue=True and a message is already showing, add to queue.
    """
    global current_message, message_timer, ui_font, message_queue

    # If text is queued and something is already being displayed
    if queue and current_message:
        message_queue.append((text, duration, size))
        return

    # Change font size per message
    ui_font = pygame.font.Font("Main/PressStart2P-Regular.ttf", size)

    current_message = text
    message_timer = time.time() + duration


# -----------------------------
# Start Menu
# -----------------------------
def start():
    """
    Loads and displays the start menu using pygame_menu.
    Plays start-menu music.
    """
    pygame.mixer.music.load("Main/start_menu_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    # Background image for start screen
    background_image = pygame_menu.baseimage.BaseImage("Main/start_background.png")

    # Menu theme styling
    my_theme = pygame_menu.Theme(
        title=False,
        background_color=background_image,
        widget_font=pygame.font.Font("Main/PressStart2P-Regular.ttf", 32),
        widget_font_size=40,
        widget_font_color=(255, 255, 255),
        widget_padding=10,
        selection_color=(255, 255, 0),
        widget_alignment=pygame_menu.locals.ALIGN_CENTER
    )

    # Highlight box around selected item
    my_theme.widget_selection_effect = pygame_menu.widgets.HighlightSelection(
        border_width=5,
        margin_x=100,
        margin_y=70
    )

    menu = pygame_menu.Menu("Welcome", width, height, theme=my_theme)

    # Start screen art
    img = menu.add.image("Main/start_select.png")

    # Blank-button trick (text hidden)
    start_button = menu.add.button("         ", game)
    quit_button = menu.add.button("         ", pygame_menu.events.EXIT)

    # Positioning of graphic/buttons
    img.translate(0, 0)
    start_button.translate(-9, -289.5)
    quit_button.translate(-9, -215)

    # Run the menu loop
    menu.mainloop(win)


# -----------------------------
# Pause Menu
# -----------------------------
def unpause():
    """Resume the game by setting paused = False."""
    global paused
    paused = False


def pause():
    """
    Opens pause menu with dark transparent background.
    Freezes gameplay until unpaused.
    """
    global paused
    paused = True

    # Play pause music
    pygame.mixer.music.load("Main/pause_menu_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    screen_surface = win.copy()

    # Pause menu theme
    my_theme = pygame_menu.Theme(
        title=False,
        background_color=(50, 50, 50, 200),   # Semi transparent overlay
        widget_alignment=pygame_menu.locals.ALIGN_CENTER,
        widget_font=pygame.font.Font("Main/PressStart2P-Regular.ttf", 32),
        widget_font_size=40,
        widget_font_color=(255, 255, 255),
        selection_color=(255, 255, 0),
    )

    my_theme.widget_selection_effect = pygame_menu.widgets.HighlightSelection(
        border_width=5,
        margin_x=105,
        margin_y=75
    )

    # Build pause menu
    pause_menu = pygame_menu.Menu("Paused", width, height, theme=my_theme)
    img = pause_menu.add.image("Main/pause_select.png")
    resume_button = pause_menu.add.button("         ", unpause)
    quit_button = pause_menu.add.button("         ", start)

    img.translate(0, 0)
    resume_button.translate(-9, -277.5)
    quit_button.translate(-9, -190)

    # Pause Loop
    while paused:
        win.blit(screen_surface, (0, 0))
        events = pygame.event.get()
        pause_menu.update(events)
        pause_menu.draw(win)
        pygame.display.update()

    pygame.mixer.music.stop()


# -----------------------------
# End Game Animation & Menu
# -----------------------------
def end():
    """
    Plays a frame-by-frame animation (15 images)
    Then opens the end-menu.
    """
    frames = [
        "Main/end_1.png", "Main/end_2.png", "Main/end_3.png", "Main/end_4.png", "Main/end_5.png",
        "Main/end_6.png", "Main/end_7.png", "Main/end_8.png", "Main/end_9.png", "Main/end_10.png",
        "Main/end_11.png", "Main/end_12.png", "Main/end_13.png", "Main/end_14.png", "Main/end_15.png"
    ]

    # Animation loop
    for frame in frames:
        img = pygame.image.load(frame).convert_alpha()
        img = pygame.transform.scale(img, (1920, 1150))
        win.blit(img, (0, 0))
        pygame.display.flip()

        # Custom frame timings
        if frame == frames[2]:
            pygame.time.delay(800)
        elif frame in (frames[11], frames[12], frames[13], frames[14]):
            time.sleep(0.0001)
        else:
            pygame.time.delay(300)

        # Start end music during first frame
        if frame == frames[0]:
            pygame.mixer.music.load("Main/end_menu_music.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)

        # Extra delay on frame 11
        if frame == frames[10]:
            pygame.time.delay(1000)

    pygame.time.delay(3000)

    # Turn last frame into background
    screen_surface = win.copy()
    pygame.image.save(screen_surface, "Main/temp_pause_bg.png")
    background_image = pygame_menu.baseimage.BaseImage("Main/temp_pause_bg.png")

    # End menu theme
    my_theme = pygame_menu.Theme(
        title=False,
        background_color=background_image,
        widget_alignment=pygame_menu.locals.ALIGN_CENTER,
        widget_font=pygame.font.Font("Main/PressStart2P-Regular.ttf", 32),
        widget_font_size=40,
        widget_font_color=(255, 255, 255),
        selection_color=(255, 255, 0),
    )

    my_theme.widget_selection_effect = pygame_menu.widgets.HighlightSelection(
        border_width=5,
        margin_x=105,
        margin_y=75
    )

    # Build end menu
    end_menu = pygame_menu.Menu("Thank you", width, height, theme=my_theme)
    img = end_menu.add.image("Main/end_select.png")
    menu_button = end_menu.add.button("         ", start)
    quit_button = end_menu.add.button("         ", pygame_menu.events.EXIT)

    img.translate(0, 0)
    menu_button.translate(-9, -277.5)
    quit_button.translate(-9, -190)

    end_menu.draw(win)
    end_menu.mainloop(win)


# -----------------------------
# Main Game Loop
# -----------------------------
def game():
    """
    The actual playable game.
    Handles movement, collisions, interaction, levels, and UI messages.
    """
    global current_message, message_timer, message_queue, ui_font

    pygame.mixer.music.stop()

    # Reset player & load level 1
    player = Player(center_x, center_y,width, height)
    level = Level(2, show_message, width, height)

    while True:
        player.resize(0.5) # Delete after placement test
        dt = clock.tick(60)

        # Check if player is near an interactable item
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

        # Player movement
        old = player.handle_input(keys)
        level.collide_player(old, player.rect)

        # Animation frame
        frame = player.animate()

        # Draw level + player
        level.draw(win, player.rect)
        win.blit(frame, (player.rect.x, player.rect.y))

        # Level complete → go to next level
        if level.is_finished():
            
            level = Level(level.level_id + 1, show_message, width, height)
            
            if level.level_id == 2:
                player.resize(0.5)
            
            player.rect.center = (center_x, center_y)

        # If level > 4 → end game
        if level.level_id > 4:
            end()
            break

        # -----------------------------
        # Text Message Box Display
        # -----------------------------
        if current_message and time.time() < message_timer:
            box_rect = pygame.Rect(0, height - 120, width, 120)
            pygame.draw.rect(win, (255, 255, 255), box_rect)
            pygame.draw.rect(win, (0, 0, 0), box_rect, 4)
            text_surface = ui_font.render(current_message, True, (0, 0, 0))
            win.blit(text_surface, (40, height - 90))

        # Message expired → load next queued message
        if current_message and time.time() >= message_timer:
            if message_queue:
                text, duration, size = message_queue.pop(0)
                ui_font = pygame.font.Font("Main/PressStart2P-Regular.ttf", size)
                current_message = text
                message_timer = time.time() + duration
            else:
                current_message = ""

        pygame.display.flip()


# -----------------------------
# Start the Game
# -----------------------------
start()
