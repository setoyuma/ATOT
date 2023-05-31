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

	def move(self, constraints):
		for constraint in constraints:
			if self.rect.colliderect(constraint.rect):
				if self.direction == 'up':
					print("at top")
					self.direction = "down"
				elif self.direction == 'down':
					print("at bottom")
					self.direction = "up"
				elif self.direction == 'right':
					print("at right")
					self.direction = "left"
				elif self.direction == 'left':
					print("at left")
					self.direction = "right"
			
			if self.direction == 'up':
				self.rect.y -= self.speed
			elif self.direction == 'down':
				self.rect.y += self.speed
			elif self.direction == 'left':
				self.rect.x -= self.speed
			elif self.direction == 'right':
				self.rect.x += self.speed

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
	