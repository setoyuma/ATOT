from saviorsystems.REDFORGE import *
from particles import ParticleEffect
from player import Player
from enemy import Enemy

class Level:
	def __init__(self, game, level_data, surface):
		
		# level setup
		self.game = game
		self.display_surface = surface 
		self.world_shift = pygame.math.Vector2()
		self.current_x = 0
		# Lighting
		self.torch_list = []
		# particles
		self.particles = []
		# dust 
		self.dust_sprite = pygame.sprite.GroupSingle()
		self.player_collide_bottom = False

		# Sprite groups setup
		self.terrain = pygame.sprite.Group()  # Terrain sprites group
		self.torches = pygame.sprite.Group()  # Torch sprites group
		self.foreground = pygame.sprite.Group()  #  Foreground group
		self.background = pygame.sprite.Group()  # Background sprites group
		self.constraints = pygame.sprite.Group()  # Constraint sprites group
		self.next_room_triggers = pygame.sprite.Group()  # Level Triggers sprites group
		self.last_room_triggers = pygame.sprite.Group()  # Level Triggers sprites group
		self.player_layer = pygame.sprite.GroupSingle()  # Player sprite group
		self.enemy_layer = pygame.sprite.Group()  # Enemy sprite group
		self.projectiles = pygame.sprite.Group()  # Projectile sprite group

		# Terrain layout
		terrain_layout = import_csv_layout(level_data['terrain'])  # Load Terrain layout from CSV
		self.create_tile_group(terrain_layout, 'terrain')  # Create Terrain tile sprites
		
		# Torch layout
		torch_layout = import_csv_layout(level_data['torch'])  # Load Torch layout from CSV
		self.create_tile_group(torch_layout, 'torch')  # Create Torch tile sprites
		
		# Foreground layout
		foreground_layout = import_csv_layout(level_data['foreground'])  # Load Foreground layout from CSV
		self.create_tile_group(foreground_layout, 'foreground')  # Create Foreground tile sprites
		
		# Background layout
		background_layout = import_csv_layout(level_data['background'])  # Load Background layout from CSV
		self.create_tile_group(background_layout, 'background')  # Create Background tile sprites
		
		# Constraint layout
		constraint_layout = import_csv_layout(level_data['constraint'])  # Load Constraint layout from CSV
		self.create_tile_group(constraint_layout, 'constraint')  # Create Constraint tile sprites
		
		# Next Level Trigger layout
		next_room_trigger_layout = import_csv_layout(level_data['next_room_trigger'])  # Load Next Level Trigger layout from CSV
		self.create_tile_group(next_room_trigger_layout, 'next_room_trigger')  # Create Next Level Trigger tile sprites
		
		# Last Level Trigger layout
		last_room_trigger_layout = import_csv_layout(level_data['last_room_trigger'])  # Load Last Level Trigger layout from CSV
		self.create_tile_group(last_room_trigger_layout, 'last_room_trigger')  # Create Last Trigger tile sprites

		# Player
		player_layout = import_csv_layout(level_data['player'])  # Load Player layout from CSV
		self.player_setup(player_layout)  # Set up the Player
		
		# Enemies
		enemy_layout = import_csv_layout(level_data['enemy'])  # Load Enemy layout from CSV
		self.enemy_setup(enemy_layout)  # Set up the Enemy

		# Order the layers of the level
		self.world_layers = [
			self.background,
			self.terrain,
			self.torches,
			self.player_layer,
			self.dust_sprite,
			self.enemy_layer,
			self.projectiles,
			self.foreground,
		]

		# Get the level size
		self.calculate_level_size()

		# Mark points of the level
		self.level_topleft = self.terrain.sprites()[0].rect
		self.level_bottomright = self.terrain.sprites()[len(self.terrain)-1].rect

		# Event Triggers
		self.last_room_triggered = False
		self.next_room_triggered = False

	def calculate_level_size(self):
		# Calculate the size of the level based on the layers
		max_right = 0
		max_bottom = 0

		for layer in self.world_layers:
			for sprite in layer:
				sprite_rect = sprite.rect
				sprite_right = sprite_rect.x + sprite_rect.width
				sprite_bottom = sprite_rect.y + sprite_rect.height

				max_right = max(max_right, sprite_right)
				max_bottom = max(max_bottom, sprite_bottom)

		self.level_width = max_right
		self.level_height = max_bottom

	def get_player_collide_bottom(self):
		if self.player.collide_bottom:
			self.player_collide_bottom = True
		else:
			self.player_collide_bottom = False

	def create_landing_dust(self):
		if not self.player_collide_bottom and self.player.collide_bottom and not self.dust_sprite.sprites():
			if self.player.facing_right:
				offset = pygame.math.Vector2(10,15)
			else:
				offset = pygame.math.Vector2(-10,15)
			fall_dust_particle = ParticleEffect(self.player.rect.midbottom - offset,'land')
			self.dust_sprite.add(fall_dust_particle)

	def create_tile_group(self, layout, tile_type):
		# Create a group of tile sprites based on the layout and type
		tile_list = import_cut_graphics('../assets/terrain/Tileset.png')  # Load tile graphics

		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				if val != '-1':
					x = col_index * TILE_SIZE
					y = row_index * TILE_SIZE

					# Use match case to handle different tile types
					match tile_type:
						case 'terrain':
							sprite = StaticTile((x, y), [self.terrain], tile_list[int(val)])
						case 'foreground':
							sprite = StaticTile((x, y), [self.foreground], tile_list[int(val)])
						case 'background':
							sprite = StaticTile((x, y), [self.background], tile_list[int(val)])
						case 'constraint':
							sprite = StaticTile((x, y), [self.constraints], tile_list[int(val)])
						case 'next_room_trigger':
							sprite = StaticTile((x, y), [self.next_room_triggers], tile_list[int(val)])
						case 'last_room_trigger':
							sprite = StaticTile((x, y), [self.last_room_triggers], tile_list[int(val)])
						case 'torch':
							self.torch_list.append(Light(50, "teal", 15))
							torch = StaticTile((x, y), self.torches, tile_list[int(val)])

	def player_setup(self, layout):
		# Set up the player based on the layout
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				if val == '0':
					self.player = Player(self.game, "ALRYN", (x, y), self.display_surface, self.player_layer)
	
	def enemy_setup(self, layout):
		# Set up the player based on the layout
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				if val == '0':
					self.enemy = Enemy("sepparition", 96, (x,y), self.terrain, self.constraints, [self.enemy_layer])

	def set_camera(self):
		self.camera = Camera(self.world_layers, self.player, self) # Set level camera

	""" HANDLERS """
	def light_handler(self):
		for torch in self.torch_list:
			torch.world_light()
			torch.apply_lighting(self.display_surface, torch.light_layer, light_source_list=self.torches)
			break
	
	def particle_handler(self):
		# Handle the particles in the level
		# Torch particles
		for torch in self.torches.sprites():
			self.particles.append(Particle(torch.rect.centerx, torch.rect.centery, '', 3, (0, 255, 255), 'torch'))

		# Draw and update particles
		for particle in self.particles:
			particle.update(self.camera)
			particle.draw(self.display_surface, self.camera)

		self.particles = [particle for particle in self.particles if not particle.is_expired()]

	def projectile_collisions(self):
		for projectile in self.projectiles.sprites():
			for enemy in self.enemy_layer.sprites():
				if projectile.rect.colliderect(enemy.rect):
					if projectile.rect.centerx > enemy.rect.centerx:
						projectile.kill()
						enemy.rect.x -= 30
						enemy.health -= 10
						print("enemy hit with projectile on right")
					elif projectile.rect.centerx < enemy.rect.centerx:
						projectile.kill()
						enemy.rect.x += 30
						enemy.health -= 10
						print("enemy hit with projectile on right")

	def constraint_handler(self):
		self.constraints.update(self.world_shift)
	
	def level_trigger_handler(self):
		self.next_room_triggers.update(self.world_shift)
		self.last_room_triggers.update(self.world_shift)

	def next_level(self):
		for sprite in self.next_room_triggers.sprites():
			if self.player.rect.colliderect(sprite.rect):
				self.next_room_triggered = True
			else:
				self.next_room_triggered = False
	
	def last_level(self):
		for sprite in self.last_room_triggers.sprites():
			if self.player.rect.colliderect(sprite.rect):
				self.last_room_triggered = True
			else:
				self.last_room_triggered = False

	def run(self):
		# level triggers
		self.level_trigger_handler()
		self.next_level()
		self.last_level()

		# handle camera
		self.set_camera()
		self.camera.scroll_x()
		self.camera.update()
		self.camera.draw_layers(self.display_surface)
		# self.camera.scroll_y()  # doesnt do what i want it to

		# constraints
		self.constraint_handler()

		# for sprite in self.constraints.sprites():
		# 	pygame.draw.rect(self.display_surface, "yellow", sprite.rect)
		
		for sprite in self.constraints.sprites():
			pygame.draw.rect(self.display_surface, "yellow", sprite.rect)

		# effects
		self.light_handler()
		self.particle_handler()
		# dust particles 
		self.create_landing_dust()

		# player
		self.player.physics.horizontal_movement_collision(self.player, self.terrain)
		self.get_player_collide_bottom()
		self.player.physics.apply_gravity(self.player, GRAVITY)
		self.player.physics.vertical_movement_collision(self.player, self.terrain)

		self.projectile_collisions()

