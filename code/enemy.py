from saviorsystems.REDFORGE import *

class Enemy(Entity):
	def __init__(self, enemy_type:str, size:int, position:tuple, terrain_tiles:pygame.sprite.Group, constraint_tiles:pygame.sprite.Group, groups:list):
		super().__init__(size, position, ENEMIES[enemy_type]["SPEED"], groups)
		self.enemy_type = enemy_type
		self.import_character_assets()
		self.frame_index = 0
		self.animation_speed = 0.15
		self.image = self.animations['run'][self.frame_index]

		self.terrain_tiles = terrain_tiles
		self.constraints = constraint_tiles

		# stats
		self.stats = ENEMIES[self.enemy_type]
		self.speed = self.stats["SPEED"]
		self.health = ENEMIES[self.enemy_type]["HEALTH"]

		# status
		self.status = 'run'
		self.aggro = False  # Used to check aggro
		self.direction = "right"
		self.directions = [
			"up",
			"down",
			"left",
			"right",
		]

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
		if self.stats["GRAVITY"]:
			self.direction = random.choice(("right", "left"))
		else:
			self.direction = random.choice(self.directions)

	def patrol(self):
		for sprite in self.constraints.sprites():
			if self.rect.colliderect(sprite.rect):
				if self.direction == "right":
					self.direction = "left"
				elif self.direction == "left":
					self.direction = "right"
				elif self.direction == "up":
					self.direction = "down"
				elif self.direction == "down":
					self.direction = "up"
				else:
					pass
					
				if self.rect.right >= sprite.rect.left:
					self.rect.right = sprite.rect.left
				elif self.rect.left <= sprite.rect.right:
					self.rect.left = sprite.rect.right
		
		match self.direction:
			case "right":
				self.velocity.x = self.speed
				self.facing_right = False
			case "left":
				self.velocity.x = -self.speed
				self.facing_right = True
			# case "up":
				# self.velocity.y = -self.speed
			# case "down":
				# self.velocity.y = self.speed

	def take_knockback(self, knockback:int, damage:int):
		if self.velocity.x < 0:
			self.velocity.x += knockback
			self.health -= damage
		elif self.velocity.x > 0:
			self.velocity.x += knockback
			self.health -= damage

	def update(self, world_shift):
		# self.get_direction()
		self.rect.x += world_shift.x
		self.patrol()
		self.get_status()
		self.animate()

		print(self.velocity.x)

		self.physics.horizontal_movement_collision(self, self.terrain_tiles)
		if self.stats["GRAVITY"] == True:
			self.physics.apply_gravity(self, GRAVITY)
		self.physics.vertical_movement_collision(self, self.terrain_tiles)

