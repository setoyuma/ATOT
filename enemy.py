import pygame as pg
from CONSTANTS import *
from support import *

class Enemy(pg.sprite.Sprite):
	def __init__(self, pos, groups, collision_sprites, direction='right'):
		super().__init__(groups)
		self.import_character_assets()
		self.index = 0  # Animation index
		self.frame_index = 0
		self.animation_speed = 0.2
		self.image = self.animations['run'][self.frame_index]  # Current image
		self.rect = pg.Rect(pos, (96,96))
		self.velocity = pg.math.Vector2(0, 0)  # Velocity vector
		self.gravity = GRAVITY  # Gravity value
		self.hit_status = 'normal'  # Status variable ('normal', 'damaged')
		self.status = 'run'
		self.health = 100  # Health value
		self.damaged_frames = 0  # Number of frames to show damage effect
		self.direction = direction  # Direction ('right', 'left')
		self.patrol_range = 200  # Distance to patrol back and forth
		self.patrol_start_pos = pos  # Starting position for patrol
		self.collision_sprites = collision_sprites
		self.collision_area = pg.Rect(0, 0, TILE_SIZE * 3, TILE_SIZE * 3)
		self.on_left = False
		self.on_right = False
		self.onGround = False
		self.onCeiling = False
		self.facing_right = False
		self.wait_frames = 60  # Number of frames to wait at each end of patrol
		self.current_wait_frames = 0  # Counter for current wait frames
		self.patrol_speed = 2  # Speed of patrol movement

		self.patrol()  # Start patrolling

	def update(self, offset):
		self.hurtboxing(offset)
		self.animate()
		self.handle_status()
		self.move()

		self.rect.x += self.velocity.x * self.patrol_speed
		self.horizontal_collisions()
		self.apply_gravity()
		self.vertical_collisions()


	def hurtboxing(self, offset):
		self.hurtbox = pg.Rect((self.rect.x - offset.x, self.rect.y - offset.y), self.image.get_size())

	def import_character_assets(self):
		enemy_path = MOSS_SENTINEL
		self.animations = {'run': []}

		for animation in self.animations.keys():
			full_path = enemy_path + animation
			self.animations[animation] = import_folder(full_path)

	def animate(self):
		animation = self.animations[self.status]

		# Loop over frame index
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		self.image = pg.transform.scale(pg.transform.flip(animation[int(self.frame_index)], False, False), (96, 96))

		if not self.facing_right:
			self.image = pg.transform.scale(pg.transform.flip(self.image, True, False), (96, 96))

	def apply_gravity(self):
		self.velocity.y += self.gravity
		self.rect.y += self.velocity.y

	def move(self):
		if self.current_wait_frames > 0:
			# Wait at the end of the patrol
			self.velocity.x = 0
			self.current_wait_frames -= 1
		else:
			# Move in the current direction
			if self.direction == 'right':
				self.velocity.x = self.patrol_speed
				self.facing_right = False
			elif self.direction == 'left':
				self.velocity.x = -self.patrol_speed
				self.facing_right = True

	def handle_status(self):
		if self.hit_status == 'damaged':
			if self.damaged_frames > 0:
				self.image.fill("white")  # Set image to white
				self.damaged_frames -= 1
			else:
				self.image = self.animations['run'][int(self.frame_index)]  # Restore original image
				self.hit_status = 'normal'

	def take_damage(self):
		if self.hit_status == 'normal':
			self.health -= 10
			self.damaged_frames = 5  # Show damaged effect for 5 frames
			self.hit_status = 'damaged'

	def patrol(self):
		if self.direction == 'right':
			if self.rect.x < self.patrol_start_pos[0] + self.patrol_range:
				self.direction = 'right'
			else:
				self.direction = 'left'
		elif self.direction == 'left':
			if self.rect.x > self.patrol_start_pos[0] - self.patrol_range:
				self.direction = 'left'
			else:
				self.direction = 'right'

	def horizontal_collisions(self):
		self.collision_area.center = self.rect.center
		sprites_to_check = [sprite for sprite in self.collision_sprites if sprite.rect.colliderect(self.collision_area)]

		for sprite in sprites_to_check:
			if sprite.rect.colliderect(self.rect):
				if self.velocity.x < 0:
					self.rect.left = sprite.rect.right
					self.direction = 'right'
					self.current_wait_frames = self.wait_frames
				if self.velocity.x > 0:
					self.rect.right = sprite.rect.left
					self.direction = 'left'
					self.current_wait_frames = self.wait_frames

		if self.on_left and (self.rect.left < self.currentX or self.velocity.x >= 0):
			self.on_left = False
		if self.on_right and (self.rect.right > self.currentX or self.velocity.x <= 0):
			self.on_right = False

	def vertical_collisions(self):
		self.collision_area.center = self.rect.center
		sprites_to_check = [sprite for sprite in self.collision_sprites if sprite.rect.colliderect(self.collision_area)]

		for sprite in sprites_to_check:
			if sprite.rect.colliderect(self.rect):
				if self.velocity.y > 0:
					self.rect.bottom = sprite.rect.top
					self.velocity.y = 0
					self.onGround = True
				if self.velocity.y < 0:
					self.rect.top = sprite.rect.bottom
					self.velocity.y = 0
					self.onCeiling = True

		# Check if still colliding with the ground or ceiling
		if not self.onGround and self.velocity.y >= 0:  # Not on the ground and moving downwards
			self.velocity.y = min(self.velocity.y + self.gravity, MAX_FALL_SPEED)
		elif not self.onCeiling and self.velocity.y < 0:  # Not on the ceiling and moving upwards
			self.velocity.y = max(self.velocity.y, -MAX_JUMP_SPEED)

		if self.onGround and self.velocity.y < 0:  # Stop jumping if already on the ground
			self.velocity.y = 0

