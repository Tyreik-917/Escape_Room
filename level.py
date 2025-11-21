import pygame
from item import Item, Statue_m, Statue_f, Picture, Door

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
                Door("door", "table.png", (0, 0), (1,1),False, False),
                Picture("picture", "picture.png", (0, height)),
                Statue_m("statue", "statue_m.png", (-200, height)),
                Statue_f("statue", "statue_f.png", (200, height)),
            ]
            #name,address, (pos) (0,0) = center, (size) * scale, collision (naturally on), interactable (naturally on)
            self.background = pygame.image.load("background.png")
        elif level_id == 2:
            self.items = [
                Door("door", "table.png", (0, 0), (1,1),False, False),
            ]  
            self.background = pygame.image.load("background.png")
        elif level_id == 3:
            self.items = [
                Door("door", "table.png", (0, 0), (1,1),False, False),
            ]  
            self.background = pygame.image.load("background.png")
        elif level_id == 4:
            self.items = [
                Door("door", "table.png", (0, 0), (1,1),False, False),
            ]  
            self.background = pygame.image.load("background.png")
        for item in self.items:
            item.set_message_callback(self.show_message)

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
        print(closest_item)

    def is_finished(self):
    # Puzzle is done if all non-door items are finished
        puzzle_done = all(item.is_finished for item in self.items if not isinstance(item, Door))
        if not puzzle_done:
            return False
        # Unlock the door(s)
        for item in self.items:
            if isinstance(item, Door):
                item.interactable = True  # persistent flag, can now interact with it
                return item.is_finished  # return True only if the door itself is finished
        return False

    
    def draw(self, surface, player_rect):
        surface.blit(self.background, (0, 0))

        for item in self.items:
            item.draw(surface, player_rect, show_hitbox=True)

    def collide_player(self, old_pos, player_rect):
        for item in self.items:
            if item.collides_with(player_rect) and item.collision==True:
                player_rect.x = old_pos.x
                player_rect.y = old_pos.y

