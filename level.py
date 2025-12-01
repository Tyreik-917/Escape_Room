import pygame
from item import Item, Carpet, Statue_m, Statue_f, Picture, Door, Chest, Shovel, Knife, Trash, MusicBox, Bookshelf

width, height = 1920//2, 1080//2
center_x, center_y = 0, 0

class Level:
    def __init__(self, level_id, show_message_callback):
        self.level_id = level_id
        self.show_message = show_message_callback

        self.items = []

        # --------------------------------------------------
        # LOAD ITEMS FOR LEVEL 1
        # --------------------------------------------------
        if level_id == 1:
            
            self.items = [
                # name, sprite,       (world position), size, collision?, interactable?
                Door("door", "level_1/trapdoor.png", (0, -100), (1.5,1.5), False, False),
                Carpet("carpet", "level_1/carpet.png", (0, -100), (1,1), False),
                Picture("picture", "level_1/picture.png", (0, height), (1,1), False, False),
                Statue_m("statue", "level_1/statue_m.png", (-200, height), (1,1), False, False),
                Statue_f("statue", "level_1/statue_f.png", (200, height), (1,1), False, False),
                Knife("knife", "level_1/knife.png", (-width+140, height-110), (1,1), False, False),
                Shovel("shovel", "level_1/shovel.png", (width-140, height-115), (1,1.5), False, False),
                Trash("trash", "level_1/trash.png", (-width, -330), (1,1), True, False),
                Chest("chest", "level_1/chest.png", (-width, -250)),
                MusicBox("music_box", "level_1/music_box.png", (-width//2 + 50, height-200), (1,1), False, False),
                Bookshelf("bookshelf", "level_1/bookshelf.png", (width, -height+350), (1,1), True, False),
            ]

            # Knife starts completed so it doesn’t block the level
            Knife.is_finished = True

            # Load background for attic level
            self.background = pygame.image.load("level_1/attic.png")

            # Intro tutorial messages
            self.show_message("Oh no, I've been kidnapped I must ESCAPE", size=32, queue=True)
            self.show_message("I can use 'W','A','S','D' to get around", size=32, queue=True)
            self.show_message("I can use 'E' to interact with my surroundings", size=32, queue=True)
            

        # --------------------------------------------------
        # LEVELS 2, 3, AND 4 (placeholder functionality)
        # --------------------------------------------------
        elif level_id == 2:
            self.items = [ Door("door", "door.png", (0, 0), (1,1), False, True) ]
            self.items = [ Dresser("dresser", "dresser.png", (0, 0), (1,1), False, True) ]
            self.background = pygame.image.load("bedroom.png")

        elif level_id == 3:
            self.items = [ Door("door", "table.png", (0, 0), (1,1), False, True) ]
            self.background = pygame.image.load("background.png")

        elif level_id == 4:
            self.items = [ Door("door", "table.png", (0, 0), (1,1), False, True) ]
            self.background = pygame.image.load("background.png")
            

        # Give each item the callback to display messages
        for item in self.items:
            item.set_message_callback(self.show_message)

        # Tracks how many puzzles were solved in this level
        self.puzzles_solved = 0

        # Give each item a reference to THIS level instance
        for item in self.items:
            item.level = self


    # ------------------------------------------------------
    # Only the closest item to the player becomes interactable
    # Handles "glowing" and "press E" hints
    # ------------------------------------------------------
    def update_interactable(self, player):
        closest_item = None
        min_distance_sq = float('inf')

        for item in self.items:
            if item.is_active and getattr(item, "interactable", True):
                dx = item.rect.centerx - player.rect.centerx
                dy = item.rect.centery - player.rect.centery
                distance_sq = dx*dx + dy*dy

                if distance_sq < min_distance_sq:
                    min_distance_sq = distance_sq
                    closest_item = item

        # Set glow + interaction availability
        for item in self.items:
            item.glow = (item == closest_item)
            item.can_interact_now = (item == closest_item)

      
    # ------------------------------------------------------
    # Checks if level puzzles are solved and unlocks the door
    # ------------------------------------------------------
    def is_finished(self):
        # Count how many items remain unsolved (not doors)
        self.remaining_puzzles = (
            sum(1 for item in self.items if not isinstance(item, Door) and not item.is_finished) - 1
        )

        # Logic for LEVEL 1's multi-step puzzle chain
        if self.level_id == 1:
            for item in self.items:

                # After folding carpet → enable trapdoor & picture
                if isinstance(item, Carpet) and item.is_finished:
                    for i in self.items:
                        if isinstance(i, Door) and i.reinteractable:
                            i.interactable = True
                        if isinstance(i, Picture) and i.reinteractable:
                            i.interactable = True

                # After viewing picture → enable statues, shovel, trash, bookshelf, music
                if isinstance(item, Picture) and item.is_finished:
                    for i in self.items:
                        if isinstance(i, Statue_m) and i.reinteractable:
                            i.interactable = True
                        if isinstance(i, Statue_f) and i.reinteractable:
                            i.interactable = True
                        if isinstance(i, Shovel):
                            i.interactable = True
                        if isinstance(i, Trash) and i.reinteractable:
                            i.interactable = True
                        if isinstance(i, Bookshelf) and i.reinteractable:
                            i.interactable = True
                        if isinstance(i, MusicBox) and i.reinteractable:
                            i.interactable = True

        # If puzzles remain → keep door locked
        if self.remaining_puzzles != 0:
            for item in self.items:
                if isinstance(item, Door):
                    item.can_open = False
            return False

        # Puzzles complete → open the door
        for item in self.items:
            if isinstance(item, Door):

                # Special trapdoor animation for level 1
                if self.level_id == 1:
                    item.image = pygame.image.load("level_1/trapdoor_open.png").convert_alpha()
                    item.image = pygame.transform.scale(item.image, item.resize)

                    if not item.can_open:  # play sound only once
                        pygame.mixer.Sound("level_1/trap_door_open.mp3").play()

                item.can_open = True
                return item.is_finished

        return False
    

    # ------------------------------------------------------
    # Draw background + all items
    # ------------------------------------------------------
    def draw(self, surface, player_rect):
        surface.blit(self.background, (0, 0))
        for item in self.items:
            item.draw(surface, player_rect, show_hitbox=False)


    # ------------------------------------------------------
    # Solid objects push player back to old position
    # ------------------------------------------------------
    def collide_player(self, old_pos, player_rect):
        for item in self.items:
            if item.collides_with(player_rect) and item.collision:
                player_rect.x = old_pos.x
                player_rect.y = old_pos.y

