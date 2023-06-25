import numpy as np
import random, time

from projectile import Projectile
from game_data import levels
from BLACKFORGE2 import *
from CONSTANTS import*

class RampTile(StaticTile):
	def __init__(self, game, position: tuple, groups: list, surface: pygame.Surface,
				 left_ramp: bool = False, right_ramp: bool = False):
		super().__init__(position, groups, surface)
		self.game = game
		self.left_ramp = left_ramp
		self.right_ramp = right_ramp

	def update(self, world_shift):
		self.rect.x += world_shift.x
		self.rect.y += world_shift.y

	def check_collision(self, player_rect):
		if self.left_ramp:
			ramp_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height // 2)
			if ramp_rect.colliderect(player_rect):
				# Adjust player's y-coordinate to match the slope of the ramp
				player_rect.y = self.rect.y + self.rect.height - (player_rect.x - self.rect.x) - player_rect.height
				return True
		elif self.right_ramp:
			ramp_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height // 2, self.rect.width, self.rect.height // 2)
			if ramp_rect.colliderect(player_rect):
				# Adjust player's y-coordinate to match the slope of the ramp
				player_rect.y = self.rect.y + (player_rect.x - self.rect.x)
				return True
		else:
			if self.rect.colliderect(player_rect):
				return True
		return False





class UI():
	def __init__(self, game, surface):
		self.game = game
		self.display = surface

		self.player_hud = get_image('../assets/ui/HUD/player_hud.png')
		self.player_hud = scale_images([self.player_hud], (320,320))[0]
	
	def update_player_HUD(self):
		# under bars
		health_under_bar = pygame.Rect((SCREEN_WIDTH-315, 165), (310, 32))
		pygame.draw.rect(self.display, [0,0,0], health_under_bar)
		
		magick_under_bar = pygame.Rect((SCREEN_WIDTH-85, 202), (80, 16))
		pygame.draw.rect(self.display, [0,0,0], magick_under_bar)
		
		spell_shard_1_socket = pygame.Rect((SCREEN_WIDTH-300, 204), (20, 18))
		pygame.draw.rect(self.display, [0,0,0], spell_shard_1_socket)
		
		spell_shard_2_socket = pygame.Rect((SCREEN_WIDTH-274, 204), (20, 18))
		pygame.draw.rect(self.display, [0,0,0], spell_shard_2_socket)

		magick_bar = pygame.Rect((SCREEN_WIDTH-80, 202), (66 * self.game.player.magick/self.game.player.magick_scale, 16))
		pygame.draw.rect(self.display, [0,150,200], magick_bar)
		# bars
		health_bar = pygame.Rect((SCREEN_WIDTH-315, 165), (310 * self.game.player.health/self.game.player.health_scale, 32))
		pygame.draw.rect(self.display, [50,0,0], health_bar)
	
		
		if self.game.player.spell_shards > 0:
			spell_shard_1 = pygame.Rect((SCREEN_WIDTH-300, 205), (30 * self.game.player.spell_shards/2, 16))
			pygame.draw.rect(self.display, [0,150,200], spell_shard_1)
		
		if self.game.player.spell_shards == 2:
			spell_shard_2 = pygame.Rect((SCREEN_WIDTH-274, 205), (20 * self.game.player.spell_shards/2, 16))
			pygame.draw.rect(self.display, [0,150,200], spell_shard_2)
		
		self.display.blit(self.player_hud, (SCREEN_WIDTH-320,0))

class Enemy(Entity):
	def __init__(self, game, enemy_type, size, position, speed, groups):
		super().__init__(size, position, speed, groups)
		self.game = game
		self.enemy_type = enemy_type

		self.hit = False
		self.damage_taken = False

		self.health = 100

		# the time it will travel in seconds
		self.knockback_distance = 0.1

		# collision area
		self.collision_area = pygame.Rect(0, 0, TILE_SIZE * 3, TILE_SIZE * 3)

	def take_damage(self, damage:int, damage_source, hit_location:tuple):
		self.hit = True
		self.damage_source = damage_source
		self.health -= damage
		self.damage_taken = True

	def knockback(self):
		if self.facing_right and self.hit and self.knockback_distance > 0:
			self.velocity.x = 8
		if not self.facing_right and self.hit and self.knockback_distance > 0:
			self.velocity.x = 8

	def update(self, dt, terrain):
		self.rect.x += self.velocity.x * dt
		self.physics.horizontal_movement_collision(self, terrain)
		self.physics.apply_gravity(self, GRAVITY, self.game.dt)
		self.rect.y += self.velocity.y * dt
		self.physics.vertical_movement_collision(self, terrain)

		if self.hit:
			self.knockback()
			self.knockback_distance -= 1 * self.game.dt
		else:
			self.velocity.x = 0
		
		if self.knockback_distance <= 0:
			self.hit = False
			self.damage_taken = False
			self.knockback_distance = 0.1

		# print(self.hit)
		# print(self.velocity.x)
		# print(self.knockback_distance)
		# print(self.knockback_distance)

class Player(Entity):
	def __init__(self, game, character:str, size:int, position:tuple, speed:int, group:pygame.sprite.Group()):
		super().__init__(size, position, speed, group)
		self.game = game
		self.character = character
		self.import_character_assets()

		self.current_x = None
		self.rect = self.image.get_rect(topleft=position)
		self.projectiles = []

		# player stats
		self.health = 100
		self.magick = 50
		self.spell_shards = 0
		self.dash_distance = 50
		self.dash_timer = 4
		self.dash_counter = 1
		self.jump_force = CHARACTERS[self.character]["JUMPFORCE"]

		# stat scales
		self.health_scale = 100
		self.magick_scale = 50
		self.spell_shard_scale = 2

		# player status
		self.status = 'idle'
		self.attacking = False
		self.dashing = False

		# animation
		self.animation = self.animations[self.status]
		self.image = self.animation.animation[0]

		# collision area
		self.collision_area = pygame.Rect(self.rect.x, self.rect.y, TILE_SIZE * 3, TILE_SIZE * 3)

	def import_character_assets(self):
		self.animations = {}
		self.animation_keys = {'idle':[],'run':[],'jump':[],'fall':[], 'attack':[]} 
		for key in self.animation_keys:
			full_path = CHAR_PATH + key
			original_images = import_folder(full_path)
			scaled_images = scale_images(original_images, self.size)
			if key in ["idle", "run"]:
				loop = True
			else:
				loop = False
			animation = Animator(self.game, scaled_images, FRAME_DURATIONS[key], loop)
			self.animations[key] = animation

	def update_animation(self):
		self.animation = self.animations[self.status]
		if self.animation.done and not self.animation.loop:
			if self.status in self.animation_keys:
				self.status = "idle"
				self.animation.reset()
				pass
		
		if self.facing_right:
			flipped_image = pygame.transform.flip(self.animation.update(self.game.dt),False,False)
			self.image = flipped_image
		else:
			flipped_image = pygame.transform.flip(self.animation.update(self.game.dt),True,False)
			self.image = flipped_image

	def jump(self, dt):
		self.velocity.y = -self.jump_force

	def move(self, dt):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_d] and not self.dashing and self.game.playable:
			self.facing_right = True
			self.velocity.x = self.speed
		elif keys[pygame.K_a] and not self.dashing and self.game.playable:
			self.facing_right = False
			self.velocity.x = -self.speed
		else:
			self.velocity.x = 0

		if keys[pygame.K_LSHIFT] and self.dash_counter > 0 and self.game.playable:
			self.dash_point = (self.rect.x, self.rect.y)
			self.dashing = True
			self.dash_counter -= 1

		if keys[pygame.K_SPACE] and self.collide_bottom:
			self.jump(dt)

		if self.attacking:
			self.attack()

	def dash(self, dt):
		frame_scale = self.game.current_fps / 60.0
		adjusted_dash_distance = self.dash_distance * frame_scale

		if self.dashing and self.facing_right and not self.collide_bottom:
			self.velocity.x += adjusted_dash_distance
			marker = pygame.Rect(self.dash_point - self.game.camera.level_scroll, (40,40))
			pygame.draw.rect(self.game.screen, "white", marker)

		elif self.dashing and not self.facing_right and not self.collide_bottom:
			self.velocity.x += -adjusted_dash_distance
			marker = pygame.Rect(self.dash_point - self.game.camera.level_scroll, (40,40))
			pygame.draw.rect(self.game.screen, "white", marker)

	def attack(self):
		if self.facing_right:
			self.true_hitbox = pygame.Rect(
				(self.rect.x + 40, 
				self.rect.y + 25), 
				(60, 40)
				)
			self.hitbox = pygame.Rect(
				((self.rect.x + 40) - self.game.camera.level_scroll.x, 
				 (self.rect.y + 25) - self.game.camera.level_scroll.y), 
				(60, 40)
				)
		elif not self.facing_right:
			self.true_hitbox = pygame.Rect(
				(self.rect.x - 13, 
				self.rect.y + 25), 
				(60, 40)
				)
			self.hitbox = pygame.Rect(
				((self.rect.x - 13) - self.game.camera.level_scroll.x, 
				 (self.rect.y + 25) - self.game.camera.level_scroll.y), 
				(60, 40)
				)
		pygame.draw.rect(pygame.display.get_surface(), "red", self.hitbox)

	def get_status(self):
		if self.velocity.y < 0:
			self.status = 'jump'
		elif self.velocity.y > 1:
			self.status = 'fall'
		else:
			if self.velocity.x != 0:
				self.status = 'run'
			else:
				self.status = 'idle'
		if self.attacking:
			self.status = 'attack'
	
	def on_screen_check(self):
		if self.rect.x >= self.game.level.level_bottomright.x:
			self.rect.x = self.game.level.level_bottomright.x
		elif self.rect.x <= self.game.level.level_topleft.x:
			self.rect.x = self.game.level.level_topleft.x

	def draw(self, surface:pygame.Surface):
		surface.blit(self.image, (self.rect.x-self.game.camera.level_scroll.x, self.rect.y-self.game.camera.level_scroll.y))

	def update(self, dt, surface:pygame.Surface, terrain:pygame.sprite.Group):
		self.move(dt)
		self.dash(dt)
		self.on_screen_check()
		self.get_status()
		self.update_animation()

		self.rect.x += self.velocity.x * dt
		self.physics.horizontal_movement_collision(self, terrain)
		self.physics.apply_gravity(self, GRAVITY, dt)
		self.rect.y += self.velocity.y * dt
		self.physics.vertical_movement_collision(self, terrain)

		# dashing
		if not self.dashing and self.dash_counter <= 0 and self.collide_bottom:
			self.dash_counter = 1

		if self.dashing and self.dash_timer > 0:
			self.dash_timer -= 1
			blur_surface = pygame.transform.box_blur(self.image, 4, True)
			self.image = blur_surface

		if self.dash_timer <= 0 or not self.dashing:
			self.dashing = False
			self.dash_timer = 4
		if self.collide_bottom:
			self.dashing = False

		# items
		if self.spell_shards > 2:
			self.spell_shards = 2

class Level():
	def __init__(self, game, level_data, surface):
		self.game = game
		self.level_data = level_data
		self.display_surface = surface

		self.light_list = []
		self.particles = []
		
		# tile setup
		self.tile_index = {}
		self.create_tile_index()
		self.create_groups()
		
		# game map
		self.draw_distance = 10

		# print(self.tile_index)
		# print(self.generate_chunk(150,500))

		# with open(level_data["terrain"], 'r') as f:
		# 	print(f.read())
		
	def create_groups(self):
		self.terrain = pygame.sprite.Group()  # Terrain sprites group
		self.ramp_tiles = pygame.sprite.Group()  # Ramp Tile sprites group
		self.lights = pygame.sprite.Group()  # light sprites group
		self.projectiles = pygame.sprite.Group()  # projectiles sprites group
		self.particles = pygame.sprite.Group()  # particles sprites group
		self.foreground = pygame.sprite.Group()  #  Foreground group
		self.background = pygame.sprite.Group()  # Background sprites group
		self.constraints = pygame.sprite.Group()  # Constraint sprites group

		for layout_name in ["terrain", "foreground", "background", "left_ramps", "right_ramps"]:
			layout = import_csv_layout(self.level_data[layout_name])
			self.create_tile_group(layout, layout_name, 64)

		# light layout
		light_layout = import_csv_layout(self.level_data['torch'])  # Load light layout from CSV
		self.create_tile_group(light_layout, 'light', 64)  # Create light tile sprites

		# Player layout
		player_layout = import_csv_layout(self.level_data['player'])  # Load Player layout from CSV
		self.player_setup(player_layout)  # Set up the Player

		self.world_layers = [
			self.background,
			self.terrain,
			self.ramp_tiles,
			# self.projectiles,
			self.game.player_group,
			self.particles,
			self.lights,
			self.foreground,
			# self.constraints
		]

		self.calculate_level_size()
		self.level_topleft = self.terrain.sprites()[0].rect
		self.level_bottomright = self.terrain.sprites()[len(self.terrain)-1].rect

	def create_tile_index(self):
		tile_list = import_cut_graphics('../assets/terrain/Tileset.png', TILE_SIZE)  # Load tile graphics
		for index, tile in enumerate(tile_list):
			self.tile_index[index] = tile

	def calculate_level_size(self):
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

	def create_tile_group(self, level_data, tile_type:str, tile_size:int):
		for row_index, row in enumerate(level_data):  # iterate over each row
			for col_index, value in enumerate(row):		# and then over each column
				if value != '-1':  # here we check if a tile should be placed
					x = col_index * tile_size
					y = row_index * tile_size

					# use match case to handle different tile types e.g(foreground/background tiles)
					match tile_type:
						case 'terrain':
							sprite = StaticTile((x, y), [self.terrain], self.tile_index[int(value)])
						case 'left_ramps':
							sprite = RampTile(self.game, (x, y), [self.ramp_tiles], self.tile_index[int(value)], left_ramp=True)
						case 'right_ramps':
							sprite = RampTile(self.game, (x, y), [self.ramp_tiles], self.tile_index[int(value)], right_ramp=True)
						case 'foreground':
							sprite = StaticTile((x, y), [self.foreground], self.tile_index[int(value)])
						case 'background':
							sprite = StaticTile((x, y), [self.background], self.tile_index[int(value)])
						case 'light':
							self.light_list.append([[x,y], 100, 30])
							light = StaticTile((x, y), self.lights, self.tile_index[int(value)])

	def player_setup(self, layout):
		# Set up the player based on the layout
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				if val == '0':
					self.player_spawn = pygame.math.Vector2(x,y)
					self.game.player = Player(self.game, "ALRYN", 96, (x, y), CHARACTERS["ALRYN"]["SPEED"], self.game.player_group)

	def respawn(self):
		if self.game.player.rect.bottom >= self.level_height + 300:
			self.game.player.rect.x = self.player_spawn.x
			self.game.player.rect.y = self.player_spawn.y
			self.game.playable = False
		if self.game.player.collide_bottom:
			self.game.playable = True

	""" HANDLERS """
	def light_handler(self):
		for light in self.light_list:
			surf = glow_surface(light[1], [0,50,100], light[2])
			pos = (int((light[0][0] - self.game.camera.level_scroll.x) - (light[1] - 30)), int((light[0][1] - self.game.camera.level_scroll.y) - light[1]/2))
			self.game.screen.blit(surf, pos, special_flags=BLEND_RGB_ADD)
			# light.world_light()
			# light.apply_lighting(self.display_surface, light.light_layer, light_source_list=self.lights)
	
	def calculate_visible_tiles(self):
		self.on_screen_tiles = pygame.sprite.Group()
		self.off_screen_tiles = pygame.sprite.Group()

		for layer in self.world_layers:
			for tile in layer.sprites():
				if self.is_tile_on_screen(tile):
					self.on_screen_tiles.add(tile)
				else:
					self.off_screen_tiles.add(tile)
					self.on_screen_tiles.remove(tile)

		return self.on_screen_tiles
		return self.off_screen_tiles

	def is_tile_on_screen(self, tile):
		screen_left = self.game.camera.level_scroll.x
		screen_right = screen_left + SCREEN_WIDTH
		screen_top = self.game.camera.level_scroll.y
		screen_bottom = screen_top + SCREEN_HEIGHT

		tile_top = tile.rect.y + self.draw_distance
		tile_left = tile.rect.x + self.draw_distance
		tile_bottom = tile.rect.y + tile.rect.height - self.draw_distance
		tile_right = tile.rect.x + tile.rect.width - self.draw_distance

		if tile_right >= screen_left and tile_left <= screen_right and tile_bottom >= screen_top and tile_top <= screen_bottom:
			return True

		return False

	def draw_level(self, surface:pygame.Surface):
		# draw on screen tiles
		for tile in self.on_screen_tiles:
			if tile in self.ramp_tiles:
				tile.check_collision(self.game.player.rect)
			
			if tile in [self.background, self.foreground, self.lights, self.off_screen_tiles]:
				tile.rect = 0
				tile.position = tile.position - self.game.camera.level_scroll
				surface.blit(tile.image, (tile.position.x, tile.position.y))
			else:
				surface.blit(tile.image, (tile.rect.x - self.game.camera.level_scroll.x, tile.rect.y - self.game.camera.level_scroll.y))

	def update_level(self):
		self.calculate_visible_tiles()
		self.respawn()

		# print("onscreen:",len(self.on_screen_tiles))
		# print("offscreen:",len(self.off_screen_tiles))

	def show_level_markers(self, surface:pygame.Surface, colors:list):
		pygame.draw.rect(surface, colors[0], self.level_topleft)
		pygame.draw.rect(surface, colors[1], self.level_bottomright)

class ParticleSystem2D():
	def __init__(self, game, system_position, N, lifespan, color, size, system_velocity=np.array([0,0]), glow=False, gravity=False, physics=False, image=None):
		self.game = game
		self.system_position = system_position
		self.lifespan = lifespan
		self.image = image
		self.color = color
		self.size = size
		self.system_velocity = system_velocity
		self.particles = np.empty(N, dtype=particle_dtype)
		self.particle_rects = []
		if N != 0:
			self.emit(N, system_position)

		self.glow = glow
		self.gravity = gravity
		# physics and state variables
		self.physics = physics
		self.physics_class = Physics()
		self.collide_left = False
		self.collide_right = False
		self.collide_top = False
		self.collide_bottom = False

	def emit(self, num_particles, pos):
		# Check if we have enough "dead" particles to reuse
		dead_particles = np.where(self.particles['lifespan'] <= 0)[0]
		num_reuse = min(num_particles, len(dead_particles))

		# Reuse dead particles
		if num_reuse > 0:
			self.particles['position'][dead_particles[:num_reuse]] = pos
			self.particles['velocity'][dead_particles[:num_reuse]] = np.random.uniform(-1, 1, (num_reuse, 2))
			self.particles['color'][dead_particles[:num_reuse]] = np.random.uniform(0, 1, (num_reuse, 4))
			self.particles['size'][dead_particles[:num_reuse]] = np.random.uniform(self.size, self.size, num_reuse)
			self.particles['lifespan'][dead_particles[:num_reuse]] = np.random.uniform(self.lifespan, self.lifespan, num_reuse)

			for _ in range(num_reuse):
				self.particle_rects.append(pygame.Rect(self.particles['position'][0][0], self.particles['position'][0][1], self.size, self.size))

		# If we still need to emit more particles, append them to the end of the array
		if num_particles > num_reuse:
			new_particles = np.zeros(num_particles - num_reuse, dtype=self.particles.dtype)
			new_particles['position'] = pos
			new_particles['velocity'] = np.random.uniform(-1, 1, (num_particles - num_reuse, 2))
			new_particles['color'] = np.random.uniform(0, 1, (num_particles - num_reuse, 4))
			new_particles['size'] = np.random.uniform(self.size, self.size, num_particles - num_reuse)
			new_particles['lifespan'] = np.random.uniform(self.lifespan, self.lifespan, num_particles - num_reuse)

			for _ in range(num_particles - num_reuse):
				pass
				# self.particle_rects.append(pygame.Rect(self.particles['position'][0][0], self.particles['position'][0][1], self.size, self.size))

			self.particles = np.concatenate((self.particles, new_particles))

	def update(self, terrain=[]):
		"""
		old_system_position = np.copy(self.system_position)
		#self.system_position = pygame.mouse.get_pos()
		shift = self.system_position - old_system_position
		self.particles['position'] += shift
		"""

		# Update particles position with their velocity
		self.particles['position'] += self.particles['velocity']

		# Apply gravity if enabled
		if self.gravity:
			gravity_acceleration = np.array([0, 0.1])  # Adjust the value as needed
			self.particles['velocity'] += gravity_acceleration

		# Then update all particles with system's velocity
		self.particles['position'] += self.system_velocity


		self.particles['lifespan'] -= 1.0

		# Create a mask of "alive" particles
		alive_mask = self.particles['lifespan'] > 0

		# Create a new array of particles that only includes alive particles
		self.particles = self.particles[alive_mask]

		if self.physics:
			self.create_rect(show_rect=False)

	def particle_handler(self):
		# dash particles
		if self.dashing:
			self.player_paticles.emit(1, self.rect.center)

	def create_rect(self, show_rect=False):
		for particle in self.particles:
			int_position = [int(x) for x in particle["position"]]
			self.rect = pygame.Rect((int_position[0], int_position[1]), (self.size*2, self.size*2))
			if show_rect:
				pygame.draw.rect(pygame.display.get_surface(), "green", self.rect)
			if self.collide_bottom:
				self.rect.bottom = 500

	def draw(self):
		for particle in self.particles:
			int_position = [int(x) for x in particle["position"]] - self.game.camera.level_scroll
			size = self.size
			pygame.draw.circle(self.game.screen, self.color, int_position, size)
			if self.glow:
				surf = glow_surface(size*2, (50,50,50), 50)
				offset_pos = (int_position[0] - size*2, int_position[1] - size*2)
				self.game.screen.blit(surf, offset_pos, special_flags=BLEND_RGB_ADD)
			else:
				pass

class Game():
	def __init__(self):
		self.setup_pygame()
		self.setup_world()
		self.player_particles = ParticleSystem2D(self, pygame.mouse.get_pos(), N=1, lifespan=60, color=(255,255,255), size=3, glow=False, gravity=True, physics=False)
		self.playable = False

	def setup_pygame(self):
		self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SCALED)
		self.scaled_display = pygame.Surface((SCREEN_SIZE[0]//3, SCREEN_SIZE[1]//3))
		self.clock = pygame.time.Clock()
		pygame.display.set_caption("ATOT")
		# pygame.display.toggle_fullscreen()

	def setup_world(self):
		self.current_level = 2
		self.player_group = pygame.sprite.GroupSingle()
		self.level = Level(self, levels[self.current_level], self.screen)
		self.enemy = Enemy(self, "moss", 96, (self.player.rect.x + 100, self.player.rect.y - 100), 1, self.level.projectiles)
		self.camera = Camera(self, 10, 100)
		self.ui = UI(self, self.screen)

		self.world_brightness = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
		self.world_brightness.convert_alpha()
		self.world_brightness.fill([WORLD_BRIGHTNESS, WORLD_BRIGHTNESS, WORLD_BRIGHTNESS])

	def draw_fps(self):
		fpsCounter = int(self.clock.get_fps())
		draw_text(self.screen, f"FPS: {fpsCounter}", [900, 20])

	def send_frame(self):
		self.screen.blit(self.world_brightness, (0,0), special_flags=BLEND_RGB_MULT)
		if self.player.dashing:
			self.player_particles.emit(1, self.player.rect.center)
		self.player_particles.update(self.level.terrain)
		self.player_particles.draw()
		# self.level.light_handler()
		# self.screen.blit(pygame.transform.scale(self.scaled_display, (SCREEN_SIZE[0], SCREEN_SIZE[1])), (0,0))
		pygame.display.flip()
		self.clock.tick(FPS)
		self.playable = True

	def handle_events(self):
		for event in pygame.event.get():
			# quit
			if event.type == pygame.QUIT:
				self.running = False

			# button clicked
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 4:  # Mouse wheel up
					pass
				elif event.button == 5:  # Mouse wheel down
					pass
				elif event.button == 1:
					self.player.attacking = True

			# button released
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					self.player.attacking = False

			# key pressed
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_f:
					pygame.display.toggle_fullscreen()
				
				# player hud testing
				if event.key == pygame.K_h:
					self.player.health -= 10
				if event.key == pygame.K_m:
					self.player.magick -= 5
				if event.key == pygame.K_s:
					self.player.spell_shards += 1

			# key released
			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_LSHIFT:
					self.player.dashing = False

	def update_background(self):
		self.screen.fill([55, 55, 92])
		
		background = get_image('../assets/background.png')
		midground = get_image('../assets/midground.png')
		foreground = get_image('../assets/foreground.png')
		full_background = [
			background,
			midground,
			foreground,
		]
		full_background = scale_images(full_background, (self.level.level_width, self.level.level_height))
		self.screen.blit(full_background[0], (0,0)-self.camera.level_scroll * 0.25)
		self.screen.blit(full_background[1], (0,0)-self.camera.level_scroll * 0.5)
		self.screen.blit(full_background[2], (0,0)-self.camera.level_scroll * 0.8)
	
	def update_foreground(self):
		pillar = get_image('../assets/melara_pillar.png')
		
		full_foreground = [
			pillar,
		]
		full_foreground = scale_images(full_foreground, (320, SCREEN_HEIGHT))
		self.screen.blit(full_foreground[0], (550, SCREEN_HEIGHT -  full_foreground[0].get_size()[1] + 100)-self.camera.level_scroll * 1.2)
	
	def run(self):
		self.running = True
		self.last_time = time.time()
		while self.running:
			self.dt = time.time() - self.last_time  # calculate the time difference
			self.dt *= 60.0   # scale the dt by the target framerate for consistency
			self.last_time = time.time()  # reset the last_time with the current time
			self.current_fps = self.clock.get_fps()
			
			self.handle_events()

			for projectile in self.player.projectiles:
				projectile.update(self.camera.level_scroll)

			self.mouse_pos = pygame.mouse.get_pos()
			
			self.camera.update_position()
			self.update_background()
			self.level.update_level()

			self.level.draw_level(self.screen)
			# self.update_foreground()
			self.player.update(self.dt, self.screen, self.level.terrain)
			self.enemy.update(self.dt, self.level.terrain)
			self.draw_fps()

			# self.mouse_rect = pygame.Rect((self.mouse_pos[0]-16, self.mouse_pos[1]-16), (32,32))
			# pygame.draw.rect(self.screen, "green", self.mouse_rect)

			if self.player.attacking:
				if self.player.true_hitbox.colliderect(self.enemy.rect):
					self.enemy.take_damage(1, self.player, self.enemy.rect.center-self.camera.level_scroll)
			
			self.ui.update_player_HUD()
			self.send_frame()

class Camera():
	def __init__(self, game, scroll_speed:int, interpolation:int):
		self.game = game
		self.player = self.game.player
		self.level_scroll = pygame.math.Vector2()
		self.scroll_speed = scroll_speed
		self.interpolation = interpolation

	def horizontal_scroll(self):
		self.level_scroll.x += ((self.player.rect.centerx - self.level_scroll.x - (HALF_WIDTH - self.player.size.x)) / self.interpolation * self.scroll_speed)

	def vertical_scroll(self):
		self.level_scroll.y += (((self.player.rect.centery - 180) - self.level_scroll.y - (HALF_HEIGHT - self.player.size.y)) / self.interpolation * self.scroll_speed)

	def pan_cinematic(self):
		pass

	def update_position(self):
		self.horizontal_scroll()
		self.vertical_scroll()

		# constrain camera movement
		if self.game.level.level_topleft.left + self.level_scroll.x < 0:
			self.level_scroll.x = 0
		elif self.game.level.level_bottomright.right - self.level_scroll.x < SCREEN_WIDTH:
			self.level_scroll.x = self.game.level.level_width - SCREEN_WIDTH
		
		if self.game.level.level_topleft.top - self.level_scroll.y > 0:
			self.level_scroll.y = 0
		elif self.game.level.level_bottomright.bottom - self.level_scroll.y < SCREEN_HEIGHT:
			self.level_scroll.y = self.game.level.level_height - SCREEN_HEIGHT

def glow_surface(radius, color, intensity):
	intensity = intensity/100
	surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
	surface.convert_alpha()
	pygame.draw.circle(surface, [intensity * value for value in color], (radius, radius), radius)
	surface.set_colorkey([0,0,0])
	return surface

if __name__ == "__main__":
	game = Game()
	game.run()
