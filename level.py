import pygame
from item import Item, Carpet, Statue_m, Statue_f, Picture, Door, Chest, Shovel, Knife, Trash, MusicBox, Bookshelf, Dresser, Microwave, Nightlight, Ladder, SmokeDetector, Color, Hammer, Hole
import ctypes
ctypes.windll.user32.SetProcessDPIAware()  # for Windows DPI scaling issues

pygame.init()
width, height = 1920, 1080
center_x, center_y = width // 2, height // 2

class Level:
    def __init__(self, level_id, show_message_callback):
        self.level_id = level_id
        self.show_message = show_message_callback
        self.items = []
        width, height = center_x, center_y
        # Load items depending on the level
        if level_id == 1:
            self.items = [
                Door("trapdoor", "Assets/trapdoor.png", (0, -100), (1.5,1.5), False, False),
                Carpet("carpet", "Assets/carpet.png", (0, -100), (1,1), False),
                Picture("picture", "Assets/picture.png", (0, height), (1,1), False, False),
                Statue_m("statue", "Assets/statue_m.png", (-200, height), (1,1), False, False),
                Statue_f("statue", "Assets/statue_f.png", (200, height), (1,1), False, False),
                Knife("knife", "Assets/knife.png", (-width+140, height-110), (1,1), False, False, never_interactable=True),
                Shovel("shovel", "Assets/shovel.png", (width-140, height-115), (1,1.5), False, False),
                Trash("trash", "Assets/trash.png", (-width, -330), (1,1), True, False),
                Chest("chest", "Assets/chest.png", (-width, -250)),
                MusicBox("music box", "Assets/music_box.png", (-width//2 + 50, height-200), (1,1), False, False),
                Bookshelf("bookshelf", "Assets/bookshelf.png", (width, -height+375), (1,1), True, False),
            ]
            Knife.is_finished = True
            self.background = pygame.image.load("Assets/attic.png").convert()
            self.show_message("Oh no, I've been kidnapped I must ESCAPE", size = 32, queue=True)
            self.show_message("I can use 'W','A','S','D' to get around", size = 32, queue=True)
            self.show_message("I can use 'E' to interact with my surroundings", size = 32, queue=True)

        elif level_id == 2:
            self.items = [
                Door("bedroom door", "Assets/bedroom_door.png", (0, 345), (1,1), False, False),
                Dresser("dresser", "Assets/dresser.png", (-400, 300), (.66,.66), True, True),
                Microwave("microwave", "Assets/microwave.png", (250, 270), (.66,.66), True, True),
                Nightlight("nightlight", "Assets/nightlight.png", (-width+30, height-300), (1,1), False, True),
                Ladder("ladder", "Assets/ladder.png", (-250, 300), (.66,1), True, True),
                SmokeDetector("smoke detector", "Assets/smoke_detector.png", (400, 370), (1,1), False, True), 
                Color("color code", "Assets/color.png", (30, 325), (1,1), False, True),
            ]
            self.background = pygame.image.load("Assets/bedroom.png").convert()
            self.background = pygame.transform.scale(self.background, (width*2, height*2))
            self.show_message("I made it downstairs, but the door is locked!", size = 32, queue=True)
            self.show_message("It looks like I need a code for the door", size = 32, queue=True)

        elif level_id == 3:
            self.items = [ 
                          Door("pit","Assets/exit.png",(-600,-360),(1,1),False,True),
                          Hammer("chest","Assets/chest.png",(0,250), (1,1), True, True),
                          Hole("hole","Assets/hole.png",(-width+150,height-300), (1,1), False, True),
                         ]
            self.background = pygame.image.load("Assets/basement.png").convert()
            self.show_message("It looks like I am in a basement now", size=32, queue=True)
            self.show_message("I wonder what the dark pit by the bottom leads to", size=32, queue=True)

        elif level_id == 4:
            self.items = [
                Door("door", "Assets/table.png", (0, 0), (1,1), False, True),
            ]
            self.background = pygame.image.load("Assets/background.png").convert()

        for item in self.items:
            item.set_message_callback(self.show_message)
            item.level = self

        self.puzzles_solved = 0

    def update_interactable(self, player):
        """Only the closest item within range becomes interactable"""
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
        # Set interactable only for the closest item
        for item in self.items:
            item.glow = (item == closest_item)
            item.can_interact_now = (item == closest_item)

    def is_finished(self):
        """Checks if all puzzles are finished and unlocks doors if necessary"""
        self.remaining_puzzles = sum(
            1 for item in self.items if not isinstance(item, Door) and not item.is_finished and not item.never_interactable
        )

        # Level 1 specific logic
        if self.level_id == 1:
            for item in self.items:
                if isinstance(item, Carpet) and item.is_finished:
                    for i in self.items:
                        if isinstance(i, Door) and i.reinteractable:
                            i.interactable = True
                        if isinstance(i, Picture) and i.reinteractable:
                            i.interactable = True
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
        if self.level_id == 2:
            for item in self.items:
                if isinstance(item, Color) and item.is_finished:
                    for i in self.items:
                        if isinstance(i, Door) and i.reinteractable:
                            i.interactable = True
        if self.remaining_puzzles != 0:
            for item in self.items:
                if isinstance(item, Door):
                    item.can_open = False
            return False

        for item in self.items:
            if isinstance(item, Door):
                if self.level_id == 1:
                    item.image = pygame.image.load("Assets/trapdoor_open.png").convert_alpha()
                    item.image = pygame.transform.scale(item.image, item.resize)
                    if not item.can_open:
                        pygame.mixer.Sound("Assets/trap_door_open.mp3").play()
                elif self.level_id == 2:
                    item.image = pygame.image.load("Assets/bedroom_door_open.png").convert_alpha()
                    item.image = pygame.transform.scale(item.image, item.resize)
                    if not item.can_open:
                        pygame.mixer.Sound("Assets/trap_door_open.mp3").play()
                item.can_open = True
                return item.is_finished
        return False

    def draw(self, surface, player_rect):
        surface.blit(self.background, (0, 0))
        for item in self.items:
            item.draw(surface, player_rect, show_hitbox=False)

    def collide_player(self, old_pos, player_rect, dx, dy):
        for item in self.items:
            if item.collision and item.collides_with(player_rect):
                # Handle X movement separately
                if dx != 0:
                    player_rect.x = old_pos.x
                # Handle Y movement separately
                if dy != 0:
                    player_rect.y = old_pos.y
