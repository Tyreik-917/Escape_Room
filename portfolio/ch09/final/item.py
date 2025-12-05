import pygame
import time
import random
from color_game import ColorMemoryGame
from whackamole import WhackAMole
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

pygame.init()
width, height = 1920, 1080
half_w = width // 2
half_h = height // 2

wine = False
feather = False
has_shovel = False


class Item:
    def __init__(self, name, image_path, pos, size=(1,1), collision=True, interactable=True, reinteractable=True, never_interactable=False):
        global barrel
        barrel = random.randint(1,3)
        self.name = name
        self.image = pygame.image.load(image_path)
        world_x, world_y = pos
        screen_x = world_x + half_w
        screen_y = half_h - world_y
        self.rect = self.image.get_rect(center=(screen_x, screen_y))
        self.collision = collision
        self.interactable = interactable
        self.never_interactable = never_interactable
        self.glow = False
        self.reinteractable = reinteractable
        resize = (self.rect.width*size[0], self.rect.height*size[1])
        self.resize = resize
        if resize != None:
            self.image = pygame.transform.scale(self.image, resize)
        self.rect = self.image.get_rect(center=(screen_x, screen_y))
        world_x = max(-half_w + self.rect.width//2, min(world_x, half_w - self.rect.width//2))
        world_y = max(-half_h + self.rect.height//2, min(world_y, half_h - self.rect.height//2))
        self.rect.center = (world_x + half_w, half_h - world_y)
        x = max(self.rect.width, 150)
        y = max(self.rect.height, 150)
        self.interact_radius = (x,y)
        self.glow_surface = self.create_glow_surface()
        self.is_active = True
        self.is_finished = False

    def create_glow_surface(self):
        glow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        glow.fill((255,255,255,100))
        return glow

    def is_near(self, player_rect):
        dx = abs(self.rect.centerx - player_rect.centerx)
        dy = abs(self.rect.centery - player_rect.centery)
        distance = (dx,dy)
        return distance[0] < self.interact_radius[0] and distance[1] < self.interact_radius[1]

    def set_message_callback(self, callback):
        self.show_message = callback

    def draw(self, surface, player_rect, show_hitbox=False):
        if not self.is_active:
            return
        surface.blit(self.image, self.rect.topleft)
        if self.is_near(player_rect) and self.interactable and self.glow and self.reinteractable:
            surface.blit(self.glow_surface, self.rect.topleft)
        if show_hitbox:
            pygame.draw.rect(surface, (0,255,0), self.rect, 2)

    def collides_with(self, other_rect):
        return self.is_active and self.rect.colliderect(other_rect)

#Specialized item types
# level 1
class Carpet(Item):
    def interact(self):
        global trapdoor_found
        trapdoor_found = True
        self.show_message("You folded the carpet and found a trapdoor!", 3)
        new_x, new_y = (0, -300)
        pos_x = new_x + half_w
        pos_y = half_h - new_y
        self.rect.center = (pos_x, pos_y)
        self.image = pygame.image.load("Assets/folded_carpet.png").convert_alpha()
        self.rect = self.image.get_rect(center=self.rect.center)
        pygame.mixer.Sound("Assets/carpet.mp3").play()
        self.is_finished = True
        self.interactable = False
        self.reinteractable = False
        

class Statue_m(Item):
    def interact(self):
        wine = globals().get('wine', False)
        if wine == False:
            self.show_message(f"The statue seems to be missing something...", 3)
        elif wine == True:
            self.show_message(f"You gave the wine to the statue. It seems satisfied.", 3)
            pygame.mixer.Sound("Assets/drink.mp3").play()
            self.level.puzzles_solved += 1
            self.is_finished = True
            self.reinteractable = False

class Statue_f(Item):
    def interact(self):
        feather = globals().get('feather', False)
        if feather == False:
            self.show_message(f"The statue seems to be missing something...", 3)
        elif feather == True:
            self.show_message(f"You gave the feather to the statue. It seems satisfied.", 3)
            pygame.mixer.Sound("Assets/swoosh.mp3").play()
            self.level.puzzles_solved += 1
            self.is_finished = True
            self.reinteractable = False

class Picture(Item):
    def interact(self):
        pygame.mixer.Sound("Assets/creak.mp3").play()
        self.level.puzzles_solved += 1
        self.show_message(f"The picture shows a man with wine and a women with a feather", 3, 30)
        self.is_finished = True

class Knife(Item):
    pass

class Shovel(Item):
    def interact(self):
        self.show_message(f"You grabed the shovel!", 3)
        global has_shovel
        has_shovel = True
        pygame.mixer.Sound("Assets/shovel.mp3").play()
        self.is_finished = True
        self.reinteractable = False
        self.is_active = False

class Trash(Item):
    def interact(self):
        pygame.mixer.stop()
        has_shovel = globals().get('has_shovel', False)
        if has_shovel == False:
            self.show_message(f"You need something to dig through the trash.", 3)
        elif has_shovel == True:
            self.show_message(f"You dug through the trash!", 3)
            pygame.mixer.Sound("Assets/trash.mp3").play(maxtime=4000)
            self.is_finished = True
            self.reinteractable = False
            self.is_active = False
            while pygame.mixer.get_busy():
                pygame.time.delay(1)

class Chest(Item):
    def interact(self):
        global wine
        wine = True
        self.show_message(f"You found wine inside the chest.", 3)
        self.is_finished = True
        self.image = pygame.image.load("Assets/chest_opened.png").convert_alpha()
        pygame.mixer.Sound("Assets/chest_opened.mp3").play()
        self.interactable = False
        self.reinteractable = False

class MusicBox(Item):
    def interact(self):
        self.music = pygame.mixer.Sound("Assets/abc's.mp3")
        self.music.set_volume(0.3)
        if not pygame.mixer.get_busy():
            self.music.play(-1)    
        else:
            pygame.mixer.stop()
        self.is_finished = True

class Bookshelf(Item):
    def interact(self):
        message_1 = "Organizing things is always easier with music"
        message_2 = "Use 'A' and 'D' to move, 'E' to select a book, and 'Ecs' to exit"
        global feather
        puzzle_active = True
        correct_order = [
            'Assets/agartha.png', 'Assets/blue_collar.png', 'Assets/domer.png', 'Assets/eye_of_rah.png',
            'Assets/how_to_aura_farm.png', 'Assets/i_need_this.png', 'Assets/mi_bombo.png',
            'Assets/thank_you.png', 'Assets/the_art_of_67.png'
        ]
        sound = [
            'Assets/agartha.mp3', 'Assets/blue_collar.mp3', 'Assets/domer.mp3', 'Assets/eye_of_rah.mp3',
            'Assets/how_to_aura_farm.mp3', 'Assets/i_need_this.mp3', 'Assets/mi_bombo.mp3',
            'Assets/thank_you.mp3', 'Assets/the_art_of_67.mp3'
        ]
        books = correct_order.copy()
        random.shuffle(books)
        book_width = 85
        book_height = 130
        spacing = 5
        width, height = 1920, 1080
        half_w, half_h = width // 2, height // 2
        book_images = [pygame.transform.scale(pygame.image.load(b).convert_alpha(),(book_width, book_height))for b in books]
        total_width = len(books) * book_width + (len(books) - 1) * spacing
        start_x = half_w - total_width // 2
        y_top = half_h
        book_positions = [(start_x + i * (book_width + spacing) + book_width // 2, y_top)for i in range(len(books))]
        order = []          # selected order
        used_books = set()  # prevents duplicates
        cursor_index = 0
        puzzle_img = pygame.image.load("Assets/bookshelf_puzzle.png").convert_alpha()
        puzzle_img = pygame.transform.scale(puzzle_img, (half_w, half_h))
        puzzle_rect = puzzle_img.get_rect(center=(half_w, half_h))
        clock = pygame.time.Clock()

        while puzzle_active:
            dt = clock.tick(60)
            screen = pygame.display.get_surface()
            self.level.draw(screen, self.level.items[0].rect)
            screen.blit(puzzle_img, puzzle_rect.topleft)
            for i, img in enumerate(book_images):
                x, y = book_positions[i]
                rect = img.get_rect(center=(x, y))
                screen.blit(img, rect)
                if i == cursor_index:
                    glow = pygame.Surface((book_width, book_height), pygame.SRCALPHA)
                    glow.fill((255, 255, 255, 100))
                    screen.blit(glow, rect.topleft)
            box_rect = pygame.Rect(0, height - 120, width, 120)
            pygame.draw.rect(screen, (255, 255, 255), box_rect)
            pygame.draw.rect(screen, (0, 0, 0), box_rect, 4)
            font = pygame.font.Font("Assets/PressStart2P-Regular.ttf", 25)
            screen.blit(font.render(message_1, True, (0, 0, 0)),(40, height - 100))
            screen.blit(font.render(message_2, True, (0, 0, 0)),(40, height - 45))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if audioplaying != True:
                        if event.key == pygame.K_ESCAPE:
                            puzzle_active = False
                        elif event.key == pygame.K_a:
                            cursor_index = max(0, cursor_index - 1)
                        elif event.key == pygame.K_d:
                            cursor_index = min(len(book_images) - 1, cursor_index + 1)
                        elif event.key == pygame.K_e:
                            selected_book = books[cursor_index]
                            target_index = len(order)
                            if selected_book not in used_books:
                                pygame.mixer.Sound(sound[correct_order.index(selected_book)]).play()
                                used_books.add(selected_book)
                                order.append(selected_book)
                                books.pop(cursor_index)
                                img = book_images.pop(cursor_index)
                                books.insert(target_index, selected_book)
                                book_images.insert(target_index, img)
                                if cursor_index < target_index:
                                    cursor_index = cursor_index
                                elif cursor_index > target_index:
                                    cursor_index += 1
                                cursor_index = max(0, min(cursor_index, len(books) - 1))
            if order == correct_order:
                self.show_message("While cleaning you found a feather within a book", 3)
                feather = True
                self.is_finished = True
                self.interactable = False
                self.reinteractable = False
                puzzle_active = False
                return
            if len(order) == len(correct_order) and order != correct_order:
                self.show_message("You're so messy, try again whenever you want.", 3)
                return
            pygame.display.flip()
            if pygame.mixer.get_busy():
                audioplaying = True
            else:
                audioplaying = False


 
# level 2
class Color(Item):
    def interact(self):
        screen = pygame.display.get_surface()
        game = ColorMemoryGame(screen)  # use your main screen
        has_red_light = globals().get('has_red_light', False)
        has_blue_light = globals().get('has_blue_light', False) 
        has_green_light = globals().get('has_green_light', False)
        has_gray_light = globals().get('has_gray_light', False)
        if has_red_light and has_blue_light and has_green_light and has_gray_light:
            won = game.run()
        else:
            self.show_message("You need to collect all 4 colored lights to play this game.", 3)
            return
        if won:
            self.show_message("You put in the correct color sequence!", 3)
            self.is_finished = True
            self.interactable = False
            self.reinteractable = False
            self.is_active = False
        else:
            self.show_message("You put in the wrong color sequence. Try again later.", 3)

        return
class Ladder(Item):
    def interact(self):
        global has_ladder
        pygame.mixer.Sound("Assets/creak.mp3").play()
        self.show_message("You grabbed a ladder", 3)
        has_ladder = True
        self.is_finished = True
        self.reinteractable = False
        self.is_active = False
class SmokeDetector(Item):
    def interact(self):
        has_ladder = globals().get('has_ladder', False)
        global has_red_light
        if has_ladder == False:
            self.show_message("It's too high up", 3)
            pygame.mixer.Sound("Assets/smoke_detector_beep.mp3").play()
        elif has_ladder == True:
            self.show_message("You took out the red blinking light", 3)
            has_red_light = True
            self.is_finished = True
            self.reinteractable = False
class Microwave(Item):
    def interact(self):
        pygame.mixer.Sound("Assets/ding.mp3").play()
        global has_green_light
        self.show_message("You ripped out a green light from the microwave's screen", 2)
        has_green_light = True
        self.is_finished = True
        self.reinteractable = False
class Dresser(Item):
    def interact(self):
        pygame.mixer.Sound("Assets/carpet.mp3").play()
        global has_gray_light
        self.show_message("You took the gray light from the lamp", 2)
        has_gray_light = True
        self.is_finished = True
        self.reinteractable = False
class Nightlight(Item):
    def interact(self):
        global has_blue_light
        self.show_message("You took the blue light from the nightlight", 2)
        has_blue_light = True
        self.is_finished = True
        self.reinteractable = False

# level 3
class Hammer(Item):
    def interact(self):
        global has_hammer
        self.show_message("You grabbed a hammer!", 3)
        has_hammer = True
        self.image = pygame.image.load("Assets/chest_opened.png").convert_alpha()
        pygame.mixer.Sound("Assets/shovel.mp3").play()

        self.is_finished = True
        self.reinteractable = False


class Hole(Item):
    def interact(self):
        hammer_status = globals().get('has_hammer', False)
        global lvl3comp
        needed_score = 15
        if not hammer_status:
            pygame.mixer.Sound("Assets/hehe.mp3").play()
            self.show_message("You might need a tool for getting rid of this", 3)

        else:
            game = WhackAMole()
            score = game.run()

            if score >= needed_score:
                self.show_message("You cleared all the moles!", 3)
                self.is_finished = True
                self.reinteractable = False
            else:
                self.show_message(f"You were unable to clear all the moles ({score}/{needed_score}).", 3)
                

# level 4
class Red_Mouse(Item):
    def interact(self):
        cheese_status = globals().get('has_cheese', False)

        if not cheese_status:
            self.show_message("Can you find my toy cheese and enter the password into the code box for me buddy", 3)
        else:
            self.show_message("You gave the cheese to Bobby. He seems satisfied.", 3)
            pygame.mixer.Sound("Assets/hehe.mp3").play()
            self.level.puzzles_solved += 1
            self.is_finished = True
            self.reinteractable = False
            
class Grey_Mouse(Item):
    def interact(self):
        pygame.mixer.Sound("Assets/hehe.mp3").play()
        self.show_message("Go replace the power unc", 3)
        self.level.puzzles_solved += 1
        self.is_finished = True
        self.reinteractable = False
            
class Cheese_man(Item):
    def interact(self):
        global has_cheese
        self.show_message("You have the cheese touch!", 3)
        has_cheese = True

        self.is_finished = True
        self.reinteractable = False
        self.is_active = False

class Barrel_1(Item):
    def interact(self):
        barrel = globals().get('barrel', 0)
        if barrel == 1:
            global battery
            battery = True

            self.show_message("You found a battery inside the barrel.", 3)

            self.is_finished = True

            self.interactable = False
            self.reinteractable = False
        else:
            self.show_message("There seems to be nothing inside this barrel.", 3)

            self.is_finished = True

            self.interactable = False
            self.reinteractable = False

class Barrel_2(Item):
    def interact(self):
        barrel = globals().get('barrel', 0)
        if barrel == 2:
            global battery
            battery = True

            self.show_message("You found a battery inside the barrel.", 3)

            self.is_finished = True

            self.interactable = False
            self.reinteractable = False
        else:
            self.show_message("There seems to be nothing inside this barrel.", 3)

            self.is_finished = True

            self.interactable = False
            self.reinteractable = False

class Barrel_3(Item):
    def interact(self):
        barrel = globals().get('barrel', 0)
        if barrel == 3:
            global battery
            battery = True

            self.show_message("You found a battery inside the barrel.", 3)

            self.is_finished = True

            self.interactable = False
            self.reinteractable = False
        else:
            self.show_message("There seems to be nothing inside this barrel.", 3)

            self.is_finished = True

            self.interactable = False
            self.reinteractable = False

class Vent_6(Item):
    def interact(self):
        global hint_found
        hint_found = True

        self.show_message("You found a clue!", 3)

        # Change sprite
        self.image = pygame.image.load("level_4/code_6.png").convert_alpha()
        
        new_width = 90   
        new_height = 90
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        
        self.rect = self.image.get_rect(center=self.rect.center)

        self.is_finished = True
        self.interactable = False
        self.reinteractable = False
        
class Vent_7(Item):
    def interact(self):
        global hint_found
        hint_found = True

        self.show_message("You found a clue!", 3)

        # Change sprite
        self.image = pygame.image.load("level_4/code_7.png").convert_alpha()
        
        new_width = 90   
        new_height = 90
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        
        self.rect = self.image.get_rect(center=self.rect.center)

        self.is_finished = True
        self.interactable = False
        self.reinteractable = False

class Code_box(Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correct_code = ["6", "7", "6", "7"]   # required sequence
        self.is_finished = False


    def interact(self):
        message_1 = "Do you hear the knocking in the vents"
        message_2 = "Use 'A' and 'D' to move, 'E' to select a key, 'Ecs' to exit, and 'Enter' to submit"

        # --- LOAD PUZZLE IMAGE ---
        """puzzle_img = pygame.image.load("level_4/key_pad.png").convert_alpha()
        puzzle_img = pygame.transform.scale(puzzle_img, (half_w, half_h))
        puzzle_rect = puzzle_img.get_rect(center=(half_w, half_h))"""

        # --- LOAD KEYS (1-9 IMAGES) ---
        key_size = (100, 100)
        key_paths = [
            f"level_4/{i}.png" for i in range(1, 10)
        ]

        key_images = [
            pygame.transform.scale(
                pygame.image.load(path).convert_alpha(),
                key_size
            ) for path in key_paths
        ]

        # --- PUZZLE VARIABLES ---
        cursor_index = 0
        code_entered = []
        puzzle_active = True
        audioplaying = False

        clock = pygame.time.Clock()
        screen = pygame.display.get_surface()

        # -----------------------------------------
        #                PUZZLE LOOP
        # -----------------------------------------
        while puzzle_active:
            dt = clock.tick(60)

            # draw background level
            if hasattr(self, "level"):
                self.level.draw(screen, self.level.items[0].rect)

            # draw keypad backdrop

            # draw keys row
            key_y =  height // 2 + 200

            for i, img in enumerate(key_images):
                x = (width//2 - 490) + i * (10+key_size[0])

                # draw highlight on selected key
                if i == cursor_index:
                    pygame.draw.rect(
                        screen,
                        (255, 255, 0),               # yellow border
                        (x - 3, key_y - 3, key_size[0] + 6, key_size[1] + 6),
                        3
                    )

                screen.blit(img, (x, key_y))
            
            box_rect = pygame.Rect(0, height - 120, width, 120)
            pygame.draw.rect(screen, (255, 255, 255), box_rect)
            pygame.draw.rect(screen, (0, 0, 0), box_rect, 4)
            font = pygame.font.Font("Assets/PressStart2P-Regular.ttf", 20)
            screen.blit(font.render(message_1, True, (0, 0, 0)),(40, height - 100))
            screen.blit(font.render(message_2, True, (0, 0, 0)),(40, height - 45))

            # show code so far
            box_rect = pygame.Rect( half_w - (width // 4), half_h - 150, width // 2, 120)
            pygame.draw.rect(screen, (255, 255, 255), box_rect)
            pygame.draw.rect(screen, (0, 0, 0), box_rect, 4)
            typed_text = "".join(code_entered)
            font = pygame.font.Font("Assets/PressStart2P-Regular.ttf", 30)
            txt_surf = font.render(typed_text, True, (0, 0, 0))
            text_rect = txt_surf.get_rect(center=box_rect.center)
            screen.blit(txt_surf, text_rect)


            # EVENTS --------------------------
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN and not audioplaying:

                    # close puzzle
                    if event.key == pygame.K_ESCAPE:
                        puzzle_active = False

                    # move left
                    elif event.key == pygame.K_a:
                        cursor_index = max(0, cursor_index - 1)

                    # move right
                    elif event.key == pygame.K_d:
                        cursor_index = min(8, cursor_index + 1)

                    # select number
                    elif event.key == pygame.K_e and len(code_entered) < len(self.correct_code):
                        number = str(cursor_index + 1)
                        code_entered.append(number)

                    elif event.key == pygame.K_RETURN:
                        if code_entered == self.correct_code:
                            self.show_message("The lock clicks open.", 3)
                            self.is_finished = True
                            self.interactable = False
                            self.reinteractable = False
                            pygame.mixer.Sound("Assets/the_art_of_67.mp3").play()
                            return

                        # wrong + full length → fail
                        if len(code_entered) == len(self.correct_code) and code_entered != self.correct_code:
                            self.show_message("Wrong code, try again.", 3)
                            return

            # update audio state
            pygame.display.flip()

class Power_Bank(Item):
    def interact(self):
        battery_status = globals().get('battery', False)

        if not battery_status:
            self.show_message("You need to find a battery to put in here", 3)
        else:
            self.show_message("You have restored power to 100%", 3)
            pygame.mixer.Sound("Assets/ding.mp3").play()
            self.level.puzzles_solved += 1
            self.is_finished = True
            self.reinteractable = False

class Barrier_1(Item):
    pass

class Barrier_2(Item):
    pass

class Barrier_3(Item):
    pass

class Barrier_4(Item):
    pass

class Barrier_5(Item):
    pass

#same for each level
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
            elif level_id == 3:
                self.show_message("Eeek!! There are moles in here!")
            else:
                self.show_message(
                    f"The door is locked. Interact with {remaining} more item(s).",
                    3
                )