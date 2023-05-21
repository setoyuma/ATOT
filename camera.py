import pygame as pg
from constants import *

class CameraGroup(pg.sprite.Group):
    def __init__(self):
        super().__init__()
        self.displaySurface = pg.display.get_surface()
        self.offset = pg.math.Vector2(0,0)
        self.layers = []

    def addLayer(self, groups):
        self.layers.append(groups)

    def customDraw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH//2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT//1.5
        
        for layer in self.layers[0]:
            for sprite in sorted(layer.sprites(), key=lambda sprite: sprite.rect.y):
                self.offsetPos = sprite.rect.topleft - self.offset
                self.displaySurface.blit(sprite.image,self.offsetPos)
                sprite.rect.x = self.offsetPos.x
                sprite.rect.y = self.offsetPos.y
                # pg.draw.rect(pg.display.get_surface(), "red", sprite.rect)
                


