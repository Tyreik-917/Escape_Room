import pygame
from item import Item, Carpet, Statue_m, Statue_f, Picture, Door, Chest, Shovel,Knife, Trash, MusicBox, Bookshelf

width, height = 1920//2, 1080//2
center_x, center_y = 0,0
class Level:
    def __init__(self, level_id, show_message_callback):
        self.level_id = level_id
        self.show_message = show_message_callback
        self.items = []
        # Load items depending on the level
        if level_id == 1:
            self.items = [
                Door("door", "trapdoor.png", (0, -100), (1.5,1.5),False, False),
                Carpet("carpet", "carpet.png", (0, -100), (1,1), False),
                Picture("picture", "picture.png", (0, height), (1,1), False, False),
                Statue_m("statue", "statue_m.png", (-200, height), (1,1), False, False),
                Statue_f("statue", "statue_f.png", (200, height), (1,1), False, False),
                Knife("knife", "knife.png", (-width+140, height-110), (1,1), False, False),
                Shovel("shovel", "shovel.png", (width-140, height-115), (1,1.5), False, False),
                Trash("trash", "trash.png", (-width, -330), (1,1), True, False),
                Chest("chest", "chest.png", (-width, -250)),
                MusicBox("music_box", "music_box.png", (-width//2 + 50, height-200), (1,1), False, False),
                Bookshelf("bookshelf", "bookshelf.png", (width, -height+350), (1,1), True, False),
            ]
            Knife.is_finished = True
            self.background = pygame.image.load("attic.png")
            self.show_message("Oh no, I've been kidnapped I must ESCAPE", size = 32, queue=True)
            self.show_message("I can use 'W','A','S','D' to get around", size = 32, queue=True)
            self.show_message("I can use 'E' to interact with my surroundings", size = 32, queue=True)
        elif level_id == 2:
            self.items = [
                Door("door", "table.png", (0, 0), (1,1),False, True),
            ]  
            self.background = pygame.image.load("background.png")
        elif level_id == 3:
            self.items = [
                Door("door", "table.png", (0, 0), (1,1),False, True),
            ]  
            self.background = pygame.image.load("background.png")
        elif level_id == 4:
            self.items = [
                Door("door", "table.png", (0, 0), (1,1),False, True),
            ]  
            self.background = pygame.image.load("background.png")
        for item in self.items:
            item.set_message_callback(self.show_message)
        self.puzzles_solved = 0
        for item in self.items:
            item.level = self


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
        self.remaining_puzzles =  sum(1 for item in self.items if not isinstance(item, Door) and not item.is_finished) - 1
        for item in self.items:
            if self.level_id == 1:
                if isinstance(item, Carpet) and item.is_finished:
                    for item in self.items:
                        if isinstance(item, Door) and item.reinteractable:
                            item.interactable = True
                        if isinstance(item, Picture) and item.reinteractable:
                            item.interactable = True
                if isinstance(item, Picture) and item.is_finished:
                    for item in self.items:
                        if isinstance(item, Statue_m) and item.reinteractable:
                            item.interactable = True
                        if isinstance(item, Statue_f) and item.reinteractable:
                            item.interactable = True
                        if isinstance(item, Shovel):
                            item.interactable = True
                        if isinstance(item, Trash) and item.reinteractable:
                            item.interactable = True
                        if isinstance(item, Bookshelf) and item.reinteractable:
                            item.interactable = True
                        if isinstance(item, MusicBox) and item.reinteractable:
                            item.interactable = True
        if self.remaining_puzzles != 0:
            for item in self.items:
                if isinstance(item, Door):
                    item.can_open = False
                    redo = True
            return False
        for item in self.items:
            if isinstance(item, Door):
                if self.level_id ==1:
                    item.image = pygame.image.load("trapdoor_open.png").convert_alpha()
                    item.image = pygame.transform.scale(item.image, item.resize)
                    if not item.can_open:
                        pygame.mixer.Sound("trap_door_open.mp3").play()
                item.can_open = True  # unlock the door
                return item.is_finished
        return False




    
    def draw(self, surface, player_rect):
        surface.blit(self.background, (0, 0))

        for item in self.items:
            item.draw(surface, player_rect, show_hitbox=False)

    def collide_player(self, old_pos, player_rect):
        for item in self.items:
            if item.collides_with(player_rect) and item.collision==True:
                player_rect.x = old_pos.x
                player_rect.y = old_pos.y