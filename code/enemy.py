from BLACKFORGE2 import *
from CONSTANTS import *

class Enemy(Entity):
	def __init__(self, game, enemy_type:str, size:int, position:tuple, terrain_tiles:pygame.sprite.Group, constraint_tiles:pygame.sprite.Group, groups:list):
		super().__init__(size, position, ENEMIES[enemy_type]["SPEED"], groups)
		self.game = game
		self.enemy_type = enemy_type
		self.import_character_assets()
		self.frame_index = 0
		self.animation_speed = 0.15
		self.image = self.animations['run'][self.frame_index]

		self.terrain_tiles = terrain_tiles
		self.constraints = constraint_tiles

		# stats
		self.flying = not ENEMIES[self.enemy_type]["GRAVITY"]
		self.stats = ENEMIES[self.enemy_type]
		self.speed = self.stats["SPEED"]
		self.health = ENEMIES[self.enemy_type]["HEALTH"]

		# timers
		self.change_direction_timer = 80

		# status
		self.status = 'run'
		self.hit = False
		self.aggro_range = pygame.Rect(self.rect.center, ENEMIES[self.enemy_type]["AGGRO RANGE"])
		self.aggro = False  # Used to check aggro
		self.directions = [
			"up",
			"down",
			"left",
			"right",
			"up-left",
			"up-right",
			"down-left",
			"down-right",
		]
		self.direction = self.get_direction()

		# physics
		self.physics = Physics()

	def import_character_assets(self):
		character_path = f'../assets/enemy/{self.enemy_type}/'
		self.animations = {'run':[],}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = scale_images(import_folder(full_path), self.size)

	def animate(self):
		animation = self.animations[self.status]

		# loop over frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		image = animation[int(self.frame_index)]
		if self.facing_right:
			self.image = image
		else:
			flipped_image = pygame.transform.flip(image,True,False)
			self.image = flipped_image

	def get_status(self):
		if self.aggro:
			print("player in aggro range")

	def get_direction(self):
		if not self.flying:
			return random.choice(("right", "left"))
		else:
			return random.choice(self.directions)
			# self.direction = random.choice(self.directions)

	def approach(self, player, world_shift):
		# set vector equal to entity's position
		player_vector = pygame.math.Vector2(player.rect.center)
		enemy_vector = pygame.math.Vector2(self.rect.center)
		
		# get distance between the vectors
		distance = self.get_vector_distance(player_vector, enemy_vector)

		print(distance)

		# determine direction to go if there is distance to be traveled
		if distance > 0:
			self.velocity = (player_vector - enemy_vector).normalize()
		# else:
		# 	self.direction = self.get_direction()
		
		# update velocity and position 
		self.velocity = self.velocity * self.speed
		self.position += self.velocity

		# apply updated position to rect
		self.rect.centerx = self.position.x + world_shift.x
		self.rect.centery = self.position.y + world_shift.y

	def get_vector_distance(self, v1, v2):
		return(v1 - v2).magnitude()

	def manage_aggro(self, world_shift):
		self.aggro_range.center = self.rect.center
		if self.game.level.player.rect.colliderect(self.aggro_range):
			print("player in aggro range")
			# self.approach(self.game.level.player, world_shift)
		pygame.draw.rect(pygame.display.get_surface(), "blue", self.aggro_range)
	
	def move(self):
		match self.direction:
			case "right":
				self.velocity.x = self.speed
				self.facing_right = False
			case "left":
				self.velocity.x = -self.speed
				self.facing_right = True
			case "up":
				self.velocity.y = -self.speed
			case "down":
				self.velocity.y = self.speed
			# Diagonals
			case "up-left":
				self.velocity.x = -self.speed
				self.velocity.y = -self.speed
			case "up-right":
				self.velocity.x = self.speed
				self.velocity.y = self.speed
			case "down-left":
				self.velocity.x = -self.speed
				self.velocity.y = self.speed
			case "down-right":
				self.velocity.x = self.speed
				self.velocity.y = self.speed
			case "stop":
				self.velocity.x = 0
				self.velocity.y = 0

	def take_knockback(self, knockback:int, damage:int):
		if self.velocity.x < 0:
			self.hit = True
			self.velocity.x += knockback
			self.health -= damage
		elif self.velocity.x > 0:
			self.hit = True
			self.velocity.x += knockback
			self.health -= damage
		else:
			self.hit = False

	def update(self, world_shift):
		print(self.change_direction_timer)
		# AGGRO
		self.manage_aggro(world_shift)
		self.rect.x += world_shift.x  # account for camera offset
		self.rect.y += world_shift.y  # account for camera offset
		self.rect.y += self.velocity.y
		self.move()
		self.get_status()
		self.animate()

		self.physics.horizontal_movement_collision(self, self.terrain_tiles)
		if self.stats["GRAVITY"] == True:
			self.physics.apply_gravity(self, GRAVITY)
		self.physics.vertical_movement_collision(self, self.terrain_tiles)

		self.change_direction_timer -= 1
		if self.change_direction_timer <= 0:
			self.direction = self.get_direction()
			self.change_direction_timer = 80



