import pygame as pg
from CONSTANTS import *
from support import *

class Tile(pg.sprite.Sprite):
	def __init__(self,pos,groups):
		super().__init__(groups)
		self.image = pg.Surface((TILE_SIZE,TILE_SIZE))
		# self.image = img
		self.image.fill(TILE_COLOR)
		self.rect = self.image.get_rect(topleft=pos)
		self.current_pos = pg.math.Vector2(pos)  # Current position of the tile
		self.start_pos = pos  # Initial position of the tile

	def move(self):
		if self.rect.top <= -100:
			# print("at top")
			self.direction = "down"
		if self.rect.bottom >= SCREEN_HEIGHT+100:
			# print("at bottom")
			self.direction = "up"

		if self.rect.right >= SCREEN_WIDTH+100:
			self.direction = "left"
		if self.rect.left <= -100:
			self.direction = "right"
		
		if self.direction == 'up':
			self.rect.y -= self.speed
		elif self.direction == 'down':
			self.rect.y += self.speed
		elif self.direction == 'left':
			self.rect.x -= self.speed
		elif self.direction == 'right':
			self.rect.x += self.speed

class StaticTile(Tile):
	def __init__(self,pos,groups,surface):
		super().__init__(pos,groups)
		self.image = surface 

class MovingTile(Tile):
	def __init__(self, pos, groups, direction, speed, surface):
		super().__init__(pos, groups)
		self.image = surface
		self.direction = direction  # Movement direction ('up', 'down', 'left', 'right')
		self.speed = speed  # Movement speed (pixels per frame)
		self.start_pos = pos  # Initial position of the tile
		self.current_pos = pg.math.Vector2(pos)  # Current position of the tile

class AnimatedTile(Tile):
	def __init__(self,size,x,y,path):
		super().__init__(size,x,y)
		self.frames = import_folder(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]

	def animate(self):
		self.frame_index += 0.15
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def update(self,shiftx,shifty):
		self.animate()
		self.rect.x += shiftx
		self.rect.y += shifty
	