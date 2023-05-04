import pygame as pg
from support import *
import random
from constants import *

class Enemy:

	def __init__(self, game, x, y, width, height):
		self.game = game
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.reset_offset = 0
		self.offset_x = random.randrange(-150, 150)
		self.offset_y = random.randrange(-150, 150)

		# state
		self.facing_right = True
		self.running = False

		# movement
		self.direction = pg.math.Vector2()

		# animations
		self.import_assets()
		self.status = 'idle'
		self.frame_index = 0
		self.animation = self.animations[self.status]
		self.image = self.animations['idle'][self.frame_index]
		self.animation_speed = 0.15

		# rect
		self.rect = self.image.get_rect(topleft = (self.x, self.y))

	def import_assets(self):
		path = "./assets/enemy/"
		self.animations = {'idle':[],'run-right':[],'run-left':[],'run-back':[], 'run':[]}

		for animation in self.animations.keys():
			full_path = path + animation
			self.animations[animation] = scale_images(import_folder(full_path), (self.width, self.height))

	def animate(self):
		animation = self.animations[self.status]

		# loop over frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0
			
		self.image = animation[int(self.frame_index)]
		if not self.facing_right:
			self.image = pg.transform.flip(self.image,True,False)

	def get_state(self):
		if self.direction.x > 0:
			self.facing_right = True
			self.running = True
			self.status = 'run-right'
		elif self.direction.x < 0:
			self.running = False
			self.facing_right = True
			self.status = 'run-left'
		elif self.direction.y > 0:
			self.running = True
			self.status = 'run'
		elif self.direction.y < 0:
			self.running = True
			self.status = 'run-back'
		else:
			self.running = False

	def main(self, display, player):
		if self.reset_offset == 0:
			self.offset_x = random.randrange(-150, 150)
			self.offset_y = random.randrange(-150, 150)
			self.reset_offset = random.randrange(120,150)
		else:
			self.reset_offset -= 1

		if player.x + self.offset_x > self.x-self.game.display_scroll.x:
			self.direction.x = 1
			self.x += ENEMY_SPEED
			self.rect.x = self.x - self.game.display_scroll.x
		elif player.x + self.offset_x < self.x-self.game.display_scroll.x:
			self.direction.x = -1
			self.x -= ENEMY_SPEED
			self.rect.x = self.x - self.game.display_scroll.x
		
		if player.y + self.offset_y > self.y-self.game.display_scroll.y:
			self.direction.y = 1
			self.y += ENEMY_SPEED
			self.rect.y = self.y - self.game.display_scroll.y
		elif player.y + self.offset_y < self.y-self.game.display_scroll.y:
			self.direction.y = -1
			self.y -= ENEMY_SPEED
			self.rect.y = self.y - self.game.display_scroll.y

		# self.get_state()
		self.animate()
		display.blit(self.image, (self.x-self.game.display_scroll.x, self.y-self.game.display_scroll.y))