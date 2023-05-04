import pygame as pg
from pygame.locals import *
import json
import math

from player_stat_line import StatLine
from animation import Animator
from pallete_swaps import *
from constants import *
from settings import *
from support import *

class Player(pg.sprite.Sprite):
	def __init__(self, game, x, y, width, height, groups, collisionSprites):
		super().__init__(groups)
		self.game = game
		self.collisionSprites = collisionSprites
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.projectiles = []

		# weapon
		# self.weapon = get_image('./assets/shotgun.png').convert_alpha()
		# self.weapon.set_colorkey((255,255,255))
		
		# state
		self.facing_right = True
		self.running = False

		# movement
		self.speed = BASE_SPEED
		self.direction = pg.math.Vector2()

		# animations
		self.import_assets()
		self.status = 'idle'
		self.frame_index = 0
		self.animation = self.animations[self.status]
		self.image = self.animations['idle'][self.frame_index]
		self.animation_speed = 0.15
		
		# rect
		self.rect = self.image.get_rect(topleft=(self.x, self.y))

	def horizontalCollisions(self):
		for sprite in self.collisionSprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if self.direction.x < 0:
					self.rect.left = sprite.rect.right
					self.on_left = True
					self.currentX = self.rect.left

				if self.direction.x > 0:
					self.rect.right = sprite.rect.left
					self.on_right = True
					self.currentX = self.rect.right

	def verticalCollisions(self):
		for sprite in self.collisionSprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if self.direction.y > 0:
					self.rect.bottom = sprite.rect.top
					self.direction.y = 0
					self.onGround = True
				if self.direction.y < 0:
					self.rect.top = sprite.rect.bottom
					self.direction.y = 0
					self.onCeiling = True

	def event_handler(self):
		keys = pg.key.get_pressed()

		if keys[pg.K_d]:
			self.game.display_scroll.x += BASE_SPEED
			self.direction.x = 1
			for proj in self.projectiles:
				proj.x += BASE_SPEED
		elif keys[pg.K_a]:
			self.game.display_scroll.x -= BASE_SPEED
			self.direction.x = -1
			for proj in self.projectiles:
				proj.x -= BASE_SPEED
		else:
			self.direction.x = 0

		if keys[pg.K_w]:
			self.direction.y = -1
			self.game.display_scroll.y -= BASE_SPEED
			for proj in self.projectiles:
				proj.y += BASE_SPEED
		elif keys[pg.K_s]:
			self.game.display_scroll.y += BASE_SPEED
			self.direction.y = 1
			for proj in self.projectiles:
				proj.y -= BASE_SPEED
		else:
			self.direction.y = 0

	def handle_weapon(self, display):
		mouseX, mouseY = pg.mouse.get_pos()
		
		rel_x, rel_y = mouseX - self.x, mouseY - self.y
		angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

		self.weapon_copy = pg.transform.rotate(self.weapon, angle)

		display.blit(self.weapon_copy, (self.x - int(self.weapon.get_width()/2), self.y + 25 - int(self.weapon_copy.get_height()/2)))

	def import_assets(self):
		path = "./assets/player/"
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

	def load_data(self):
		with open(f"./player_data/players/{self.player_name}.json",'r') as f:
			self.data = json.load(f)

	def save_data(self):
		with open(f"./player_data/players/{self.player_name}.json",'w') as f:
			json.dump(self.data, f, indent=4)	

	def main(self, display):
		self.get_state()
		self.animate()
		self.event_handler()
		# self.rect.x += self.direction.x * self.speed
		# self.horizontalCollisions()
		# self.rect.y += self.direction.y * self.speed
		# self.verticalCollisions()
		# self.handle_weapon(display)
		# self.image = blue_ebonheart(self.image)  # pallet swapped ebonheart