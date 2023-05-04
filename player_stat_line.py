import pygame as pg
from support import *


class StatLine():
    def __init__(self, text, size, player, location, color, surf):
        self.text = text
        self.x = location[0]
        self.y = location[1]
        self.size = size
        self.player = player
        self.color = color
        self.display_surface = surf
        self.hp_bar = pg.Rect(self.x-68, self.y, 100, 10)

    def draw(self):
        pg.draw.rect(self.display_surface, "lime", self.hp_bar)

    def update(self):
        self.draw()