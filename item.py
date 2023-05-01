import pygame as pg
from support import *
from settings import *


class Item(pg.sprite.Sprite):

	def __init__(self, pos, player, groups):
		super().__init__(groups)
		self.pos = pos
		self.player = player
		self.display_surface = pg.display.get_surface()
		self.image = pg.transform.scale(get_image('./assets/items/iron-dagger/iron-dagger.png'), (64,64))
		self.rect = self.image.get_rect(center=self.pos)
		pg.draw.rect(self.display_surface, "pink", self.rect)

	