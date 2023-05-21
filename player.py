import pygame as pg
from constants import *
from support import *

class Player(pg.sprite.Sprite):
	def __init__(self,pos,groups,collisionSprites,surface):
		super().__init__(groups)
		self.import_character_assets()

		self.image = pg.Surface((TILE_SIZE//2,TILE_SIZE))
		self.frame_index = 0
		self.image = self.animations['idle'][self.frame_index]
		
		self.rect = pg.Rect(pos, (96,96))
		self.pos = pg.math.Vector2(pos)

		self.spawnx = pos[0]
		self.spawny = pos[1]

		# stats
		self.hp = 100

		# state
		self.animation_speed = 0.18
		self.status = 'idle'
		self.on_left = False
		self.on_right = False
		self.hitBoxOn = False
		self.currentX = None
		self.wallJump = False

		# movement
		self.direction = pg.math.Vector2()
		self.speed = 6
		self.gravity = 0.65
		self.jumpHeight = 15  # jump speed
		self.collisionSprites = collisionSprites
		self.onGround = False
		self.onCeiling = False
		self.facing_right = True
		self.airBorne = False
		self.wallJumpCounter = 1

	def import_character_assets(self):
		character_path = './assets/character/'
		self.animations = {'idle':[],'run':[],'jump':[],'fall':[],'attack':[],'wallJump':[],}
		
		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)

	def animate(self):
		animation = self.animations[self.status]

		# loop over frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0
			
		self.image = pg.transform.scale(pg.transform.flip(animation[int(self.frame_index)],True,False), (96,96))
		if not self.facing_right:
			self.image = pg.transform.scale(pg.transform.flip(self.image,True,False), (96,96))

	def get_status(self):
		if self.direction.y < 0:
			self.status = 'jump'
		elif self.direction.y > 1 and self.onGround == False:
			 self.status = 'fall'
		elif self.direction.x != 0 and self.onGround:
			 self.status = 'run'
		else:
			 if self.direction.y == 0 and self.onGround:
				 self.status = 'idle'

		if self.onGround:
			self.airBorne = False
		else:
			self.airBorne = True

		if self.onGround == False and self.on_left:
			self.status = 'wallJump'
		if self.onGround == False and self.on_right:
			self.status = 'wallJump'
			
	def input(self):
		keys = pg.key.get_pressed()

		if keys[pg.K_d]:
			self.direction.x = 1
			self.facing_right = True
		elif keys[pg.K_a]:
			self.direction.x = -1
			self.facing_right = False
		else:
			self.direction.x = 0

		if keys[pg.K_SPACE] and self.onGround:
			self.direction.y = -self.jumpHeight
		
		'''WALL JUMP'''
		if self.onGround == False:

			if self.direction.y > -3 :
				if keys[pg.K_SPACE] and self.wallJumpCounter != 0:
					if self.on_left:
						self.wallJump = True
						self.direction.y = -self.jumpHeight
						self.wallJumpCounter -= 1

			if self.direction.y > -3 :
				if keys[pg.K_SPACE] and self.wallJumpCounter != 0:
					if self.on_right:
						self.wallJump = True
						self.direction.y = -self.jumpHeight
						self.wallJumpCounter -= 1

		if self.onGround:
			self.wallJumpCounter = 1

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
		if self.on_left and (self.rect.left < self.currentX or self.direction.x >= 0):
			self.on_left = False
		if self.on_right and (self.rect.right > self.currentX or self.direction.x <= 0):
			self.on_right = False

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

		if self.onGround and self.direction.y < 0 or self.direction.y > 1:
			self.onGround = False
		if self.onCeiling and self.direction.y > 0.1:
			self.onCeiling = False
	
	def applyGravity(self):
		self.direction.y += self.gravity
		self.rect.y += self.direction.y
		self.hurtbox.y += self.direction.y

	def hurtboxing(self):
		self.hurtbox = pg.Rect(self.rect.center, (self.image.get_width()/2, self.image.get_height()))
		self.hurtbox.center = self.rect.center
		# pg.draw.rect(pg.display.get_surface(), "white", self.hurtbox)

	def update(self):
		self.animate()
		self.input()
		self.get_status()

		self.hurtboxing()

		self.rect.x += self.direction.x * self.speed
		self.hurtbox.x += self.direction.x * self.speed
		
		self.horizontalCollisions()
		self.applyGravity()
		self.verticalCollisions()

		print(self.hurtbox.x)

		# pg.draw.rect(pg.display.get_surface(), "black", self.rect)
		# pg.draw.rect(pg.display.get_surface(), "white", self.hurtbox)
		
