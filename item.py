# item.py
import pygame
import time
import random

# Screen constants (shared with the rest of the game)
width = 1920
height = 1080
half_w = width // 2
half_h = height // 2

# Global game flags used by certain puzzles
wine = False
feather = False
has_shovel = False


# ----------------------------------------------------------
# BASE ITEM CLASS
# ----------------------------------------------------------
class Item:
    """
    Base class for all interactable objects in every level.
    
    Handles:
    - Positioning & conversion from world coords → screen coords
    - Collision
    - Interaction radius
    - Glow when near
    - Optional resizing
    """

    def __init__(self, name, image_path, pos, size=(1,1),
                 collision=True, interactable=True, reinteractable=True):

        self.name = name

        # Load the sprite
        self.image = pygame.image.load(image_path)
        
        # Convert world-position (0,0 center-based) into screen coordinates
        world_x, world_y = pos
        screen_x = world_x + half_w
        screen_y = half_h - world_y

        # Rect centered at given position
        self.rect = self.image.get_rect(center=(screen_x, screen_y))

        # Item properties
        self.collision = collision
        self.interactable = interactable
        self.reinteractable = reinteractable
        self.near_start = None   # time player entered interact radius
        self.glow = False        # glow when player is near
        self.is_active = True    # item disappears when disabled
        self.is_finished = False # used by puzzles

        # Resize item if needed
        resize = (self.rect.width * size[0], self.rect.height * size[1])
        self.resize = resize
        if resize is not None:
            self.image = pygame.transform.scale(self.image, resize)

        # Update rect after resizing
        self.rect = self.image.get_rect(center=(screen_x, screen_y))

        # Clamp item inside world boundaries
        world_x = max(-half_w + self.rect.width//2,
                      min(world_x, half_w - self.rect.width//2))
        world_y = max(-half_h + self.rect.height//2,
                      min(world_y, half_h - self.rect.height//2))

        # Reposition clamped coordinates back into screen space
        self.rect.center = (world_x + half_w, half_h - world_y)

        # Interaction radius: depends on size of object (min 150)
        x = max(self.rect.width, 150)
        y = max(self.rect.height, 150)
        self.interact_radius = (x, y)

        # Semi-transparent glow overlay when player is nearby
        self.glow_surface = self.create_glow_surface()


    # ----------------------------------------------------------
    # UTILITY FUNCTIONS
    # ----------------------------------------------------------
    def create_glow_surface(self):
        """Creates white, translucent glow overlay."""
        glow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        glow.fill((255, 255, 255, 100))
        return glow

    def is_near(self, player_rect):
        """
        Checks if player is within interaction radius (not circular; x/y box).
        """
        dx = abs(self.rect.centerx - player_rect.centerx)
        dy = abs(self.rect.centery - player_rect.centery)
        return dx < self.interact_radius[0] and dy < self.interact_radius[1]

    def set_message_callback(self, callback):
        """
        Connects the global message system to each item.
        """
        self.show_message = callback

    def draw(self, surface, player_rect, show_hitbox=False):
        """
        Draws item (and glow when near).
        Also shows auto-message after 10 seconds of standing near.
        """
        if not self.is_active:
            return

        # Draw item sprite
        surface.blit(self.image, self.rect.topleft)

        # Show glow when near
        if (self.is_near(player_rect)
            and self.interactable
            and self.glow
            and self.reinteractable):
            
            # Highlight glow overlay
            surface.blit(self.glow_surface, self.rect.topleft)

            # Start timer for proximity message
            if self.near_start is None:
                self.near_start = time.time()

            # Show message after 10 seconds near item
            if time.time() - self.near_start >= 10:
                self.show_message(f"You can interact with {self.name} (press E)")

        else:
            # Player left radius → reset timer
            self.near_start = None

        # Optional: draw hitbox for debugging
        if show_hitbox:
            pygame.draw.rect(surface, (0, 255, 0), self.rect, 2)

    def collides_with(self, other_rect):
        """Simple AABB collision check."""
        return self.is_active and self.rect.colliderect(other_rect)



# ----------------------------------------------------------
# SPECIALIZED ITEM TYPES — LEVEL 1
# ----------------------------------------------------------

# -------------------------------
# Carpet: reveals trapdoor
# -------------------------------
class Carpet(Item):
    def interact(self):
        """
        Folds carpet, reveals trapdoor, plays sound.
        """
        global trapdoor_found
        trapdoor_found = True

        self.show_message("You folded the carpet and found a trapdoor!", 3)

        # Move folded carpet
        new_x, new_y = (0, -300)
        pos_x = new_x + half_w
        pos_y = half_h - new_y
        self.rect.center = (pos_x, pos_y)

        # Change sprite
        self.image = pygame.image.load("folded_carpet.png").convert_alpha()
        self.rect = self.image.get_rect(center=self.rect.center)

        pygame.mixer.Sound("carpet.mp3").play()

        self.is_finished = True
        self.interactable = False
        self.reinteractable = False



# -------------------------------
# Male Statue — needs wine
# -------------------------------
class Statue_m(Item):
    def interact(self):
        wine_status = globals().get('wine', False)

        if not wine_status:
            self.show_message("The statue seems to be missing something...", 3)
        else:
            self.show_message("You gave the wine to the statue. It seems satisfied.", 3)
            pygame.mixer.Sound("drink.mp3").play()
            self.level.puzzles_solved += 1
            self.is_finished = True
            self.reinteractable = False



# -------------------------------
# Female Statue — needs feather
# -------------------------------
class Statue_f(Item):
    def interact(self):
        feather_status = globals().get('feather', False)

        if not feather_status:
            self.show_message("The statue seems to be missing something...", 3)
        else:
            self.show_message("You gave the feather to the statue. It seems satisfied.", 3)
            pygame.mixer.Sound("swoosh.mp3").play()
            self.level.puzzles_solved += 1
            self.is_finished = True
            self.reinteractable = False



# -------------------------------
# Picture — gives puzzle hint
# -------------------------------
class Picture(Item):
    def interact(self):
        pygame.mixer.Sound("creak.mp3").play()
        self.level.puzzles_solved += 1
        self.show_message(
            "The picture shows a man with wine and a woman with a feather",
            3, 30
        )
        self.is_finished = True



# -------------------------------
# Knife — placeholder item
# -------------------------------
class Knife(Item):
    pass



# -------------------------------
# Shovel — lets you dig trash
# -------------------------------
class Shovel(Item):
    def interact(self):
        global has_shovel
        self.show_message("You grabbed the shovel!", 3)
        has_shovel = True

        pygame.mixer.Sound("shovel.mp3").play()

        self.is_finished = True
        self.reinteractable = False
        self.is_active = False



# -------------------------------
# Trash — requires shovel
# -------------------------------
class Trash(Item):
    def interact(self):
        shovel_status = globals().get('has_shovel', False)

        if not shovel_status:
            self.show_message("You need something to dig through the trash.", 3)

        else:
            self.show_message("You dug through the trash!", 3)
            pygame.mixer.Sound("trash.mp3").play(maxtime=4000)

            self.is_finished = True
            self.reinteractable = False
            self.is_active = False

            # Wait for sound to finish before continuing
            while pygame.mixer.get_busy():
                pygame.time.delay(1)



# -------------------------------
# Chest — gives wine
# -------------------------------
class Chest(Item):
    def interact(self):
        global wine
        wine = True

        self.show_message("You found wine inside the chest.", 3)

        self.is_finished = True
        self.image = pygame.image.load("chest_opened.png").convert_alpha()
        pygame.mixer.Sound("chest_opened.mp3").play()

        self.interactable = False
        self.reinteractable = False



# -------------------------------
# Music Box — plays/pauses loop
# -------------------------------
class MusicBox(Item):
    def interact(self):
        self.music = pygame.mixer.Sound("abc's.mp3")
        self.music.set_volume(0.3)

        # Toggle music playback
        if not pygame.mixer.get_busy():
            self.music.play(-1)
        else:
            pygame.mixer.stop()

        self.is_finished = True



# -------------------------------
# Bookshelf Puzzle — complex minigame
# -------------------------------
class Bookshelf(Item):
    """
    Starts the book-order puzzle:
    - Books must be selected in the correct sequence
    - Plays audio clues
    - Awards feather if puzzle solved
    """

    def interact(self):
        message_1 = "Organizing things is always easier with music"
        message_2 = "Use 'A' and 'D' to move, 'E' to select a book, and 'Esc' to exit"

        global feather

        puzzle_active = True

        # Correct order of books
        correct_order = [
            'agartha.png', 'blue_collar.png', 'domer.png', 'eye_of_rah.png',
            'how_to_aura_farm.png', 'i_need_this.png', 'mi_bombo.png',
            'thank_you.png', 'the_art_of_67.png'
        ]

        # Sound for each book
        sound = [
            'agartha.mp3', 'blue_collar.mp3', 'domer.mp3', 'eye_of_rah.mp3',
            'how_to_aura_farm.mp3', 'i_need_this.mp3', 'mi_bombo.mp3',
            'thank_you.mp3', 'the_art_of_67.mp3'
        ]

        # Randomized book order
        books = correct_order.copy()
        random.shuffle(books)

        # Book visual settings
        book_width = 85
        book_height = 130
        spacing = 5

        width, height = 1920, 1080
        half_w, half_h = width // 2, height // 2

        book_images = [
            pygame.transform.scale(
                pygame.image.load(b).convert_alpha(),
                (book_width, book_height)
            ) for b in books
        ]

        # Calculate shelf layout
        total_width = len(books) * book_width + (len(books) - 1) * spacing
        start_x = half_w - total_width // 2
        y_top = half_h

        book_positions = [
            (start_x + i * (book_width + spacing) + book_width // 2, y_top)
            for i in range(len(books))
        ]

        # Puzzle tracking
        order = []         # Final selected list
        used_books = set() # Prevent selecting same book twice
        cursor_index = 0

        # Puzzle background
        puzzle_img = pygame.image.load("bookshelf_puzzle.png").convert_alpha()
        puzzle_img = pygame.transform.scale(puzzle_img, (half_w, half_h))
        puzzle_rect = puzzle_img.get_rect(center=(half_w, half_h))

        clock = pygame.time.Clock()

        # -------------------------
        # MAIN PUZZLE LOOP
        # -------------------------
        while puzzle_active:
            dt = clock.tick(60)
            screen = pygame.display.get_surface()

            # Redraw level behind puzzle
            self.level.draw(screen, self.level.items[0].rect)

            # Draw puzzle backdrop
            screen.blit(puzzle_img, puzzle_rect.topleft)

            # Draw each book and highlight the cursor
            for i, img in enumerate(book_images):
                x, y = book_positions[i]
                rect = img.get_rect(center=(x, y))
                screen.blit(img, rect)

                # Highlight current selection
                if i == cursor_index:
                    glow = pygame.Surface((book_width, book_height), pygame.SRCALPHA)
                    glow.fill((255, 255, 255, 100))
                    screen.blit(glow, rect.topleft)

            # Controls info box
            box_rect = pygame.Rect(0, height - 120, width, 120)
            pygame.draw.rect(screen, (255, 255, 255), box_rect)
            pygame.draw.rect(screen, (0, 0, 0), box_rect, 4)

            font = pygame.font.Font("PressStart2P-Regular.ttf", 25)
            screen.blit(font.render(message_1, True, (0, 0, 0)), (40, height - 100))
            screen.blit(font.render(message_2, True, (0, 0, 0)), (40, height - 45))

            # INPUT HANDLING
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif event.type == pygame.KEYDOWN:
                    if audioplaying != True:

                        # Exit puzzle
                        if event.key == pygame.K_ESCAPE:
                            puzzle_active = False

                        # Move left
                        elif event.key == pygame.K_a:
                            cursor_index = max(0, cursor_index - 1)

                        # Move right
                        elif event.key == pygame.K_d:
                            cursor_index = min(len(book_images) - 1, cursor_index + 1)

                        # Select book
                        elif event.key == pygame.K_e:
                            selected_book = books[cursor_index]
                            target_index = len(order)

                            if selected_book not in used_books:
                                # Play that book’s sound
                                pygame.mixer.Sound(sound[correct_order.index(selected_book)]).play()
                                used_books.add(selected_book)
                                order.append(selected_book)

                                # Move selected book into final slot
                                books.pop(cursor_index)
                                img = book_images.pop(cursor_index)

                                books.insert(target_index, selected_book)
                                book_images.insert(target_index, img)

                                # Adjust cursor
                                if cursor_index > target_index:
                                    cursor_index += 1
                                cursor_index = max(0, min(cursor_index, len(books) - 1))

            # PUZZLE COMPLETED CORRECTLY
            if order == correct_order:
                self.show_message("While cleaning you found a feather within a book", 3)
                feather = True
                self.is_finished = True
                self.interactable = False
                self.reinteractable = False
                puzzle_active = False
                return

            # PUZZLE FINISHED BUT WRONG
            if len(order) == len(correct_order) and order != correct_order:
                self.show_message("You're so messy, try again whenever you want.", 3)
                return

            pygame.display.flip()

            # Track whether audio is currently playing
            audioplaying = pygame.mixer.get_busy()



# ----------------------------------------------------------
# GENERAL DOOR — USED IN EVERY LEVEL
# ----------------------------------------------------------
class Door(Item):
    def interact(self):
        """
        Door only opens if all puzzles are solved.
        Shows message based on remaining puzzle count.
        """
        remaining = getattr(self.level, "remaining_puzzles", None)
        level_id = self.level.level_id

        if self.can_open:
            self.is_finished = True
            self.show_message("You open the door...", 2)
        else:
            # Special message for level 1 hint
            if remaining == 8 and level_id == 1:
                self.show_message(
                    "The door is locked. Maybe have a look at that weird painting",
                    3, 30
                )
            else:
                self.show_message(
                    f"The door is locked. Interact with {remaining} more item(s).",
                    3
                )
