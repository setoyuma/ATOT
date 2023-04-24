import pygame as pg
import json
from settings import *
from xp_targets import xp_targets
from player_stat_line import StatLine
from pygame.locals import *
from projectile import Projectile

class Player(pg.sprite.Sprite):
	
	def __init__(self, pos, groups, collisionSprites, surface):
		super().__init__(groups)
		self.player_stat_sheet = self.get_stat_sheet()
		self.collisionSprites = collisionSprites
		self.groups = groups
		# stats
		self.xp_targets = xp_targets
		self.hp = 100
		self.mana = 100
		self.projectiles = []

		self.display_surface = surface
		self.spawn_x = pos[0]
		self.spawn_y = pos[1]
		self.image = pg.image.load('./assets/races/Ebonheart.png')
		scaled_image = pg.transform.scale(self.image, (128,128))
		self.image = scaled_image
		# self.rect = self.image.get_rect()
		self.rect = pg.Rect((self.spawn_x, self.spawn_y), (128, 128))
		# self.image = pg.Surface((TILE_SIZE//2, TILE_SIZE))
		# movement
		self.direction = pg.math.Vector2()
		self.speed = BASE_SPEED

		# state vars
		self.running = False
		self.dashing = False
		self.attacking = False
		self.on_left = False
		self.on_right = False

	def horizontalCollisions(self):
		for sprite in self.collisionSprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if self.direction.x < 0:
					self.rect.left = sprite.rect.right
					self.on_left = True
					self.currentX = self.rect.left
					# print(f'touching left: {self.on_left}')

				if self.direction.x > 0:
					self.rect.right = sprite.rect.left
					self.on_right = True
					self.currentX = self.rect.right
					# print(f'touching right: {self.on_right}')
		# if self.on_left and (self.rect.left < self.currentX or self.direction.x >= 0):
		# 	self.on_left = False
		# if self.on_right and (self.rect.right > self.currentX or self.direction.x <= 0):
		# 	self.on_right = False

	def verticalCollisions(self):
		for sprite in self.collisionSprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if self.direction.y > 0:
					self.rect.bottom = sprite.rect.top
					self.direction.y = 0
					# self.onGround = True
				if self.direction.y < 0:
					self.rect.top = sprite.rect.bottom
					self.direction.y = 0
					self.onCeiling = True

			# if self.onGround and self.direction.y != 0:
			#     self.onGround = False
		
		# if self.onGround and self.direction.y < 0 or self.direction.y > 1:
		# 	self.onGround = False
		# if self.onCeiling and self.direction.y > 0.1:
		# 	self.onCeiling = False

	def event_handler(self):

		pass

		keys = pg.key.get_pressed()

		# if keys[pg.K_d]:
		# 	self.direction.x = 1
		# elif keys[pg.K_a]:
		# 	self.direction.x = -1
		# else:
		# 	self.direction.x = 0

		# if keys[pg.K_w]:
		# 	self.direction.y = -1
		# elif keys[pg.K_s]:
		# 	self.direction.y = 1
		# else:
		# 	self.direction.y = 0

		# if keys[pg.K_p]:
		# 	self.attacking = True
		# 	print('attack')

		# if keys[pg.K_u]:
		# 	# self.xp_up()
		# 	print("wow")

		# if self.running and keys[pg.K_LSHIFT]:
		# 	self.speed = BASE_SPEED + 3
		# else:
		# 	self.speed = BASE_SPEED

	def get_state(self):
		if self.direction.x != 0:
			self.running = True
		if self.direction.y != 0:
			self.running = True

	def get_stat_sheet(self):
		with open('./player_stats.json', 'r') as f:
			self.player_stats = json.load(f)
		return self.player_stats

	def check_stats(self, stat_sheet):
		if stat_sheet["XP"] == self.xp_targets[stat_sheet["Level"]]:
			self.level_up()

	def xp_up(self):
		with open('./player_stats.json', 'r') as f:
			self.player_stats = json.load(f)

		new_player_stats = {
			"XP" : int(self.player_stats["XP"]) + 1,
			"Level": int(self.player_stats["Level"])
		}

		with open('./player_stats.json', 'w') as f:
			f.write(json.dumps(new_player_stats))
			f.close()
	
	def level_up(self):

		player_stats = {
			"XP" : 0,
			"Level": self.player_stat_sheet["Level"]+1 
		}

		with open('./player_stats.json', 'w') as f:
			f.write(json.dumps(player_stats))
			f.close()

	def update(self):
		self.event_handler()
		self.rect.x += self.direction.x * self.speed
		self.horizontalCollisions()
		self.rect.y += self.direction.y * self.speed
		self.verticalCollisions()
		self.player_stat_sheet = self.get_stat_sheet()
		self.get_state()