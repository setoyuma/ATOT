import pygame as pg
from support import import_folder
from settings import TILE_SIZE


class Tile(pg.sprite.Sprite):
    def __init__(self, size, x, y, groups):
        super().__init__(groups)
        self.image = pg.Surface((size, size))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = x
        self.y = y


class DecorationTile(Tile):
    def __init__(self, size, x, y, surface, groups):
        super().__init__(size, x, y, groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=(x, y))


class StaticTile(Tile):
    def __init__(self, size, x, y, surface, groups):
        super().__init__(size, x, y, groups)
        self.image = surface


class AnimatedTile(Tile):
    def __init__(self, size, x, y, groups, path):
        super().__init__(size, x, y, groups)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()
