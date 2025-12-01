import pygame
from item import Item, Carpet, Statue_m, Statue_f, Picture, Door, Chest, Shovel, Knife, Trash, MusicBox, Bookshelf, Red_Mouse, Grey_Mouse, Cheese_man, Emty_Barrel, Barrel, Vent_6, Vent_7, Code_box, Power_Bank

class Level:
    def __init__(self, level_id, show_message_callback, screen_width, screen_height):
        self.level_id = level_id
        self.show_message = show_message_callback
        self.width = screen_width
        self.height = screen_height
        self.half_w = self.width // 2
        self.half_h = self.height // 2

        self.items = []

        # --------------------------------------------------
        # LOAD ITEMS FOR LEVEL 1
        # --------------------------------------------------
        if level_id == 1:
              
            self.items = [
            Door("door", "level_1/trapdoor.png", (0 , -100),
                size=(1.5, 1.5), collision=False, interactable=False,
                screen_width=self.width, screen_height=self.height),

            Carpet("carpet", "level_1/carpet.png", (0 , -100),
                size=(1, 1), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height),

            Picture("picture", "level_1/picture.png", (50, self.height),
                    size=(1, 1), collision=False, interactable=False,
                    screen_width=self.width, screen_height=self.height),

            Statue_m("statue_m", "level_1/statue_m.png", (-150, self.height),
                    size=(1, 1), collision=False, interactable=False,
                    screen_width=self.width, screen_height=self.height),

            Statue_f("statue_f", "level_1/statue_f.png", (250, self.height),
                    size=(1, 1), collision=False, interactable=False,
                    screen_width=self.width, screen_height=self.height),

            Knife("knife", "level_1/knife.png", (-self.width + 150, 450),
                size=(1, 1), collision=False, interactable=False,
                screen_width=self.width, screen_height=self.height),

            Shovel("shovel", "level_1/shovel.png", (self.width - 150, 450),
                size=(1, 1.5), collision=False, interactable=False,
                screen_width=self.width, screen_height=self.height),
            
            Trash("trash", "level_1/trash.png", (-self.width, -330),
                size=(1, 1), collision=True, interactable=False,
                screen_width=self.width, screen_height=self.height),

            Chest("chest", "level_1/chest.png", (-self.width, -200),
                size=(1, 1), collision=True, interactable=True,
                screen_width=self.width, screen_height=self.height),

            MusicBox("music_box", "level_1/music_box.png", (-350,300),
                    size=(1, 1), collision=False, interactable=False,
                    screen_width=self.width, screen_height=self.height),

            Bookshelf("bookshelf", "level_1/bookshelf.png",
                    (self.width, -self.height + 500),
                    size=(1, 1), collision=True, interactable=False,
                    screen_width=self.width, screen_height=self.height),
            ]


             # Knife starts completed so it doesn’t block the level
            for it in self.items:
                if isinstance(it, Knife):
                    it.is_finished = True

            # Load background for attic level
            self.background = pygame.image.load("level_1/attic.png").convert_alpha()
            self.background = pygame.transform.scale(self.background, (self.width, self.height))


            # Intro tutorial messages
            self.show_message("Oh no, I've been kidnapped I must ESCAPE", size=32, queue=True)
            self.show_message("I can use 'W','A','S','D' to get around", size=32, queue=True)
            self.show_message("I can use 'E' to interact with my surroundings", size=32, queue=True)
            

        # --------------------------------------------------
        # LEVELS 2, 3, AND 4 (placeholder functionality)
        # --------------------------------------------------
        elif level_id == 2: #Test for level 4

            
            self.items = [
                Door("door", "Main/exit.png", (-130 , self.height - 660),
                size=(0.1, 0.1), collision=False, interactable=False,
                screen_width=self.width, screen_height=self.height),
                
                Vent_6("vent", "level_4/vent.png", (85 , 100),
                size=(0.8, 0.8), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height),
                
                Vent_7("vent", "level_4/vent.png", (-30 , - self.height - 75),
                size=(0.8, 0.8), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height),
                
                Vent_6("vent", "level_4/vent.png", (-610 , self.height - 780),
                size=(0.8, 0.8), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height),
                
                Vent_7("vent", "level_4/vent.png", (460 , self.height - 1000),
                size=(0.8, 0.8), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height),
                
                Code_box("code_box", "level_4/Pipe_line.png", (-230 , self.height - 680),
                size=(0.1, 0.1), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height),
                
                Power_Bank("power_bank", "level_4/power_bank.png", (640 , self.height - 680),
                size=(0.09, 0.09), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height),
                
                Cheese_man("cheese_toy", "level_4/Mr_Cheese.png.gif", (60 , - self.height - 75),
                size=(0.1, 0.1), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height),
                
                Grey_Mouse("grey_mouse", "level_4/Grey_Mouse.png", (70, self.height - 685),
                size=(0.13, 0.13), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height),
                
                Red_Mouse("red_mouse", "level_4/Red_Mouse.png", (360, self.height - 685),
                size=(0.13, 0.13), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height),
                
                Barrel("barrel", "level_4/Barrel.png", (640 , self.height - 960),
                size=(0.8, 0.8), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height),
                
                Emty_Barrel("barrel", "level_4/Barrel.png", (-750 , self.height - 755),
                size=(0.8, 0.8), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height),
                
                Emty_Barrel("barrel", "level_4/Barrel.png", (-130 , -self.height + 620),
                size=(0.8, 0.8), collision=False, interactable=True,
                screen_width=self.width, screen_height=self.height)
                ]   
            
            self.background = pygame.image.load("level_4/sewer.png").convert_alpha()
            self.background = pygame.transform.scale(self.background, (self.width, self.height))


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
