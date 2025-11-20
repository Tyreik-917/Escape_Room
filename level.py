import pygame
from item import Item, Table, Crate, Statue

class Level:
    def __init__(self, level_id):
        self.level_id = level_id

        # Load items depending on the level
        if level_id == 1:
            self.items = [
                Table("table", "table.png", (0, 0),(1,1),False),
                Crate("crate", "crate.png", (200, 400), (.5, .5),True, False),
                Statue("statue", "statue.png", (1000, 0))    
            ]
            self.background = pygame.image.load("background.png")
        elif level_id == 2:
            self.items = [
                
            ]  
            self.background = pygame.image.load("bedroom.png")
        elif level_id == 3:
            self.items = [

            ]  
            self.background = pygame.image.load("background.png")
        elif level_id == 4:
            self.items = [

            ]  
            self.background = pygame.image.load("background.png")

    def is_finished(self):
        return all((not getattr(item, "interactable", True)) or getattr(item, "is_finished", False) for item in self.items)
    
    def draw(self, surface, player_rect):
        surface.blit(self.background, (0, 0))

        for item in self.items:
            item.draw(surface, player_rect, show_hitbox=True)

    def collide_player(self, old_pos, player_rect):
        for item in self.items:
            if item.collides_with(player_rect) and item.collision==True:
                player_rect.x = old_pos.x
                player_rect.y = old_pos.y

