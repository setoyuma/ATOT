import pygame as pg
from CONSTANTS import *
from support import *
from light import Light

class Player(pg.sprite.Sprite):
	def __init__(self, game, pos, groups, collisionSprites, surface):
		super().__init__(groups)
		self.import_character_assets()

		self.frame_index = 0
		self.image = self.animations['idle'][self.frame_index]

		self.pos = pg.math.Vector2(pos)
		self.rect = pg.Rect(self.pos, (96, 96))

		self.spawnx = pos[0]
		self.spawny = pos[1]

		# fx
		self.player_lights = []

		# stats
		self.hp = 100

		# state
		self.animation_speed = 0.2
		self.status = 'idle'
		self.on_left = False
		self.on_right = False
		self.currentX = None
		self.wallJump = False
		self.heavy_fall = False
		self.on_moving_tile = False

		# movement
		self.dash_length = 10
		self.direction = pg.math.Vector2()
		self.speed = 7
		self.gravity = GRAVITY
		self.jumpHeight = 12  # jump speed
		self.onGround = False
		self.onCeiling = False
		self.facing_right = True
		self.airBorne = False
		self.wallJumpCounter = 2

		# Collision detection
		self.collisionSprites = collisionSprites
		self.collision_area = pg.Rect(0, 0, TILE_SIZE * 3, TILE_SIZE * 3)

	def import_character_assets(self):
		character_path = ALRYN_PATH
		self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'attack': [], 'wallJump': [], 'heavyFall': []}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)

	def animate(self):
		animation = self.animations[self.status]

		# loop over frame index
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		self.image = pg.transform.scale(pg.transform.flip(animation[int(self.frame_index)], False, False),(96, 96))

		if not self.facing_right:
			self.image = pg.transform.scale(pg.transform.flip(self.image, True, False), (96, 96))

	def get_status(self):

		if self.direction.y < 0:
			self.status = 'jump'
		elif self.direction.y > 1 and not self.onGround:
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

		if not self.onGround and self.on_left:
			self.status = 'wallJump'
		if not self.onGround and self.on_right:
			self.status = 'wallJump'

		if self.direction.y >= 25:
			self.heavy_fall = True

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
		else:
			self.direction.y = self.direction.y
			
		if keys[pg.K_LSHIFT]:
			for _ in range(self.dash_length * 2):
				self.rect.x += 1

		'''WALL JUMP'''
		if not self.onGround:
			if self.direction.y > -3:
				if keys[pg.K_SPACE] and self.wallJumpCounter != 0:
					if self.on_left:
						self.wallJump = True
						self.direction.y = -self.jumpHeight
						self.wallJumpCounter -= 1

			if self.direction.y > -3:
				if keys[pg.K_SPACE] and self.wallJumpCounter != 0:
					if self.on_right:
						self.wallJump = True
						self.direction.y = -self.jumpHeight
						self.wallJumpCounter -= 1

		if self.onGround:
			self.wallJumpCounter = 2

	def horizontalCollisions(self):
		self.collision_area.center = self.rect.center
		sprites_to_check = [sprite for sprite in self.collisionSprites if sprite.rect.colliderect(self.collision_area)]

		for sprite in sprites_to_check:
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
		self.collision_area.center = self.rect.center
		sprites_to_check = [sprite for sprite in self.collisionSprites if sprite.rect.colliderect(self.collision_area)]

		for sprite in sprites_to_check:
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

	def player_light(self):
		self.player_lights.append(Light(64, "red", 15, manual_pos=(self.rect.x + 20, self.rect.y + 20)))

		for light in self.player_lights:
			light.apply_lighting(pg.display.get_surface())
			break

	def applyGravity(self):
		self.direction.y += self.gravity
		self.rect.y += self.direction.y
		self.hurtbox.y += self.direction.y

	def hurtboxing(self, offset):
		self.hurtbox = pg.Rect((self.rect.x - offset.x, self.rect.y - offset.y), (self.image.get_width() // 2, self.image.get_height()))
		self.hurtbox.center = self.rect.center - offset

	def update(self, offset):
		self.animate()
		self.input()
		self.get_status()

		self.hurtboxing(offset)

		self.rect.x += self.direction.x * self.speed
		self.hurtbox.x += self.direction.x * self.speed

		

		self.horizontalCollisions()
		self.applyGravity()
		self.verticalCollisions()

		# pg.draw.rect(pg.display.get_surface(), "white", self.collision_area)

		# self.player_light()

		# pg.draw.rect(pg.display.get_surface(), "black", self.rect)
		pg.draw.rect(pg.display.get_surface(), "white", self.hurtbox)
