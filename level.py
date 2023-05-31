import pygame as pg
from CONSTANTS import *
from tile import *
from player import Player
from support import *
from ui import UI
from camera import Camera
from particle import *
from light import Light
from enemy import Enemy

class Level:
	def __init__(self, game, level_data):
		# Initialize the Level object
		self.game = game

		# Level setup
		self.displaySurface = pg.display.get_surface()  # Get the display surface
		self.world_shift = pg.math.Vector2()  # Vector for shifting the world

		# Sprite groups setup
		self.terrain = pg.sprite.Group()  # Terrain sprites group
		self.torches = pg.sprite.Group()  # Torch sprites group
		self.movingPlats = pg.sprite.Group()  # Moving platform sprites group
		self.foreground = pg.sprite.Group()  # Foreground sprites group
		self.constraints = pg.sprite.Group() # Constraint Sprite group
		self.player_layer = pg.sprite.GroupSingle()  # Player sprite group
		self.enemy_layer = pg.sprite.Group() # Enemy Sprite Group
		self.activeSprites = pg.sprite.Group()  # Sprites in the level that will be updated
		self.collisionSprites = pg.sprite.Group()  # Sprites that the player can collide with

		self.world_layers = [
			self.terrain,
			self.torches,
			self.movingPlats,
			self.player_layer,
			self.enemy_layer,
			self.foreground,
		]  # List of sprite groups for managing different layers of the level

		# Particles
		self.particles = []  # List to store particle objects

		# Lights
		self.light_list = []  # List to store light objects

		# Moving platforms
		self.moving_platforms = []  # List to store moving platform objects

		# Terrain layout
		terrain_layout = import_csv_layout(level_data['terrain'])  # Load terrain layout from CSV
		self.create_tile_group(terrain_layout, 'terrain')  # Create terrain tile sprites
		
		# Constraint layout
		constraints_layout = import_csv_layout(level_data['constraints'])  # Load constraints layout from CSV
		self.create_tile_group(constraints_layout, 'constraints')  # Create constraints tile sprites

		# Lights layout
		self.torches_layout = import_csv_layout(level_data['lights'])  # Load torches layout from CSV
		self.create_tile_group(self.torches_layout, 'lights')  # Create torch tile sprites

		# Foreground layout
		foreground_layout = import_csv_layout(level_data['foreground'])  # Load foreground layout from CSV
		self.create_tile_group(foreground_layout, 'foreground')  # Create foreground tile sprites

		# MovingPlats layout
		movingPlats_layout = import_csv_layout(level_data['movingPlats'])  # Load movingPlats layout from CSV
		self.create_tile_group(movingPlats_layout, 'movingPlats')  # Create moving platform tile sprites

		# Player
		player_layout = import_csv_layout(level_data['player'])  # Load player layout from CSV
		self.player_setup(player_layout)  # Set up the player
		
		# Enemy
		enemy_layout = import_csv_layout(level_data['enemy'])  # Load enemy layout from CSV
		self.enemy_setup(enemy_layout)  # Set up the player

		# Calculate the size of the level based on the layers
		self.calculate_level_size()

		# Create the scroll bounds based on the level size
		scroll_bounds = pg.Rect((0, 0), (self.level_width - 100, self.level_height - 100))

		# Camera
		self.camera = Camera(self.player_layer.sprite, scroll_bounds)  # Create camera object
		self.camera.add_layer(self.world_layers)  # Add world layers to the camera

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

		self.level_width = max(max_right, MAP_WIDTH)
		self.level_height = max(max_bottom, MAP_HEIGHT)

	def create_tile_group(self, layout, tile_type):
		# Create a group of tile sprites based on the layout and type
		tile_list = import_cut_graphics('./assets/terrain/Tileset.png')  # Load tile graphics

		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				if val != '-1':
					x = col_index * TILE_SIZE
					y = row_index * TILE_SIZE

					# Use match case to handle different tile types
					match tile_type:
						case 'terrain':
							sprite = StaticTile((x, y), [self.terrain, self.collisionSprites], tile_list[int(val)])
						case 'foreground':
							sprite = StaticTile((x, y), self.foreground, tile_list[int(val)])
						case 'movingPlats':
							sprite = MovingTile((x, y), [self.movingPlats, self.collisionSprites], 'right', 3, tile_list[int(val)])
							self.moving_platforms.append(sprite)
						case 'lights':
							sprite = StaticTile((x, y), [self.torches, ], tile_list[int(val)])
						case 'constraints':
							sprite = Tile((x,y), [self.constraints])

					self.activeSprites.add(sprite)

	def player_setup(self, layout):
		# Set up the player based on the layout
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				if val == '0':
					self.player = Player(self.game, (x, y), [self.player_layer], self.collisionSprites, self.displaySurface)
	
	def enemy_setup(self, layout):
		# Set up the player based on the layout
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				if val == '0':
					enemy = Enemy((x,y), [self.enemy_layer], self.collisionSprites)

	def player_handler(self):
		self.player.update(self.camera.offset)

	def enemy_handler(self):
		for enemy in self.enemy_layer.sprites():
			enemy.update(self.camera.offset)

	def light_handler(self):
		# Handle the lights in the level
		self.light_list.append(Light(50, 'teal', 15))

		for light in self.light_list:
			light.apply_lighting(self.displaySurface, self.camera, self.torches)
			break

	def particle_handler(self):
		# Handle the particles in the level
		# Torch particles
		for torch in self.torches.sprites():
			self.particles.append(Particle(torch.rect.centerx, torch.rect.centery, '', 3, (255, 255, 255), 'torch'))

		# Draw and update particles
		for particle in self.particles:
			particle.update()
			particle.draw(self.displaySurface, self.camera)

		self.particles = [particle for particle in self.particles if not particle.is_expired()]

	def platform_handler(self):
		# Handle the moving platforms in the level
		for platform in self.moving_platforms:
			platform.move(self.constraints)

	def camera_handler(self):
		# Handle the camera in the level
		self.camera.update()
		self.camera.draw()

	def run(self):
		# Run the level update functions
		self.camera_handler()
		self.player_handler()
		self.enemy_handler()
		self.platform_handler()
		self.particle_handler()
		self.light_handler()
