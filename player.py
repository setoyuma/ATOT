import pygame as pg
from pygame.locals import *
import json

from player_stat_line import StatLine
from animation import Animator
from pallete_swaps import *
from CONSTANTS import *
from settings import *
from support import *

class Player(pg.sprite.Sprite):
	def __init__(self, game, data, pos, groups, collisionSprites, surface):
		super().__init__(groups)
		self.game = game
		self.groups = groups
		self.collisionSprites = collisionSprites

		# stats
		self.data = data
		self.stats = data["stats"]
		self.player_name = data["username"].capitalize()
		self.player_class = data["class"].capitalize()
		self.hp = 100
		self.mana = 100
		self.projectiles = []
		self.items = []

		self.display_surface = surface
		self.spawn_x = pos[0]
		self.spawn_y = pos[1]
		self.size = 64
		self.rect = pg.Rect((self.spawn_x, self.spawn_y), (64, 64))

		# movement
		self.direction = pg.math.Vector2()
		self.speed = BASE_SPEED
		
		
		# animations
		self.import_character_assets()
		self.status = 'idle'
		self.frame_index = 0
		self.animation = self.animations[self.status]
		self.image = self.animations['idle'][self.frame_index]
		self.animation_speed = 0.15

		# state vars
		self.casting_projectile = False
		self.running = False
		self.dashing = False
		self.attacking = False
		self.on_left = False
		self.on_right = False
		self.facing_right = False

	def import_character_assets(self):
		with open('./player_data/players/Setoichi.json', 'r') as file:
			player_data = json.load(file)
		
		character_path = f'./assets/races/8bit/{player_data["race"]}/'
		self.animations = {'idle':[],'run-right':[],'run-left':[],'run-back':[], 'run':[]}
		
		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = scale_images(import_folder(full_path), (self.size, self.size))
			# print(self.animations[animation])

	def animate(self):
		animation = self.animations[self.status]
		# self.hitbox = pg.Rect((self.groups[0].offsetPos.x + 20, self.groups[0].offsetPos.y), (60,98))

		# loop over frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0
			
		self.image = animation[int(self.frame_index)]
		if not self.facing_right:
			self.image = pg.transform.flip(self.image,True,False)

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
			self.direction.x = 1
		elif keys[pg.K_a]:
			self.direction.x = -1
		else:
			self.direction.x = 0

		if keys[pg.K_w]:
			self.direction.y = -1
		elif keys[pg.K_s]:
			self.direction.y = 1
		else:
			self.direction.y = 0

	def get_state(self):
		if self.direction.x > 0:
			self.running = True
			self.facing_right = True
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

	def level_up(self, stat, level_increase=1):
		if int(self.stats["xporb"]) > 0:
			if stat in self.stats.keys():
				self.stats["xporb"] -= 1
				self.stats[stat] + level_increase
				self.save_data()
			else:
				print("Not an available stat")
		else:
			print("Not enough XP orbs to level up")

	def xp_up(self, xp_amount):
		if xp_amount >= 25:
			self.stats["xp"] += xp_amount
			self.stats["xporb"] += 1
		else:
			self.stats["xp"] += xp_amount
		self.save_data()
	
	def change_rank(self):
		for rank, xp_target in ranks.items():
			if self.stats["xp"] > xp_target:
				self.data["rank"] = rank
		
	def load_data(self):
		with open(f"./player_data/players/{self.player_name}.json",'r') as f:
			self.data = json.load(f)

	def save_data(self):
		with open(f"./player_data/players/{self.player_name}.json",'w') as f:
			json.dump(self.data, f, indent=4)	

	def update(self):
		self.animate()
		self.event_handler()
		self.rect.x += self.direction.x * self.speed
		self.horizontalCollisions()
		self.rect.y += self.direction.y * self.speed
		self.verticalCollisions()
		self.get_state()
		self.change_rank()
		self.vel_x = self.direction.x * self.speed
		self.vel_y = self.direction.y * self.speed
		# self.image = blue_ebonheart(self.image)  # pallet swapped ebonheart