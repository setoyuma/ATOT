import numpy as np
import random

from projectile import Projectile
from game_data import levels
from BLACKFORGE2 import *
from CONSTANTS import*

class Camera():
	def __init__(self, game, interpolation:int):
		self.game = game
		self.player = self.game.player
		self.level_scroll = pygame.math.Vector2()
		self.interpolation = interpolation

	def horizontal_scroll(self):
		self.level_scroll.x += (self.player.rect.centerx - self.level_scroll.x - (HALF_WIDTH - self.player.size.x)) / self.interpolation

	def vertical_scroll(self):
		self.level_scroll.y += ((self.player.rect.centery - 80) - self.level_scroll.y - (HALF_HEIGHT - self.player.size.y)) / self.interpolation

	def update_position(self):
		self.horizontal_scroll()
		self.vertical_scroll()

class Player(Entity):
	def __init__(self, game, character:str, size:int, position:tuple, speed:int, group:pygame.sprite.Group()):
		super().__init__(size, position, speed, group)
		self.game = game
		self.character = character
		self.import_character_assets()
		self.frame_index = 0
		self.animation_speed = 0.25
		self.image = self.animations['idle'][self.frame_index]
		self.rect = self.image.get_rect(topleft=position)
		self.projectiles = []

		# player stats
		self.dash_timer = 10
		self.dash_counter = 1
		self.jump_force = CHARACTERS[self.character]["JUMPFORCE"]

		# player status
		self.status = 'idle'
		self.attacking = False
		self.dashing = False

	def import_character_assets(self):
		self.animations = {'idle':[],'run':[],'jump':[],'fall':[]}
		for animation in self.animations.keys():
			full_path = CHAR_PATH + animation
			self.animations[animation] = scale_images(import_folder(full_path), self.size)

	def animate(self):
		animation = self.animations[self.status]

		# loop over frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		image = animation[int(self.frame_index)]

		if self.facing_right:
			flipped_image = pygame.transform.flip(image,False,False)
			self.image = flipped_image
		else:
			flipped_image = pygame.transform.flip(image,True,False)
			self.image = flipped_image

	def move(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_d]:
			self.facing_right = True
			self.velocity.x = self.speed
		elif keys[pygame.K_a]:
			self.facing_right = False
			self.velocity.x = -self.speed
		else:
			self.velocity.x = 0

		# the Entity class has atttributes to verify where a collision is happening.
		if keys[pygame.K_SPACE] and self.collide_bottom:
			self.velocity.y = self.jump_force

		if self.attacking:
			self.attack()

	def dash(self):
		if self.dashing and self.facing_right and not self.collide_bottom:
			self.velocity.x += self.speed * 2
		elif self.dashing and not self.facing_right and not self.collide_bottom:
			self.velocity.x -= self.speed * 2

	def attack(self):
		if self.facing_right:
			hitbox = pygame.Rect(
				((self.rect.x + 40) - self.game.camera.level_scroll.x, 
				 (self.rect.y + 25) - self.game.camera.level_scroll.y), 
				(60, 40)
				)
		elif not self.facing_right:
			hitbox = pygame.Rect(
				((self.rect.x - 13) - self.game.camera.level_scroll.x, 
				 (self.rect.y + 25) - self.game.camera.level_scroll.y), 
				(60, 40)
				)
		pygame.draw.rect(pygame.display.get_surface(), "red", hitbox)

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
	
	def on_screen_check(self):
		if self.rect.x >= self.game.level.level_bottomright.x:
			self.rect.x = self.game.level.level_bottomright.x
		elif self.rect.x <= self.game.level.level_topleft.x:
			self.rect.x = self.game.level.level_topleft.x

	def draw(self, surface:pygame.Surface):
		surface.blit(self.image, (self.rect.x-self.game.camera.level_scroll.x, self.rect.y-self.game.camera.level_scroll.y))

	def update(self, surface:pygame.Surface, terrain:pygame.sprite.Group):
		self.move()
		self.on_screen_check()
		self.get_status()
		self.animate()
		self.dash()
		self.rect.x += self.velocity.x
		self.physics.horizontal_movement_collision(self, terrain)  
		self.physics.apply_gravity(self, GRAVITY) 
		self.physics.vertical_movement_collision(self, terrain)

		# dashing
		if not self.dashing and self.dash_counter <= 0 and self.collide_bottom:
			self.dash_counter = 1

		if self.dashing and self.dash_timer > 0:
			self.dash_timer -= 1

		if self.dash_timer <= 0 or not self.dashing:
			self.dashing = False
			self.dash_timer = 10

class Level():
	def __init__(self, game, level_data, surface):
		self.game = game
		self.level_data = level_data
		self.display_surface = surface

		self.light_list = []
		self.particles = []
		self.create_groups()
		self.world_layers = [
			self.background,
			self.terrain,
			self.projectiles,
			self.game.player_group,
			self.particles,
			self.lights,
			self.foreground,
			self.constraints
		]

		self.calculate_level_size()
		self.level_topleft = self.terrain.sprites()[0].rect
		self.level_bottomright = self.terrain.sprites()[len(self.terrain)-1].rect

	def create_groups(self):
		self.terrain = pygame.sprite.Group()  # Terrain sprites group
		self.lights = pygame.sprite.Group()  # light sprites group
		self.projectiles = pygame.sprite.Group()  # projectiles sprites group
		self.particles = pygame.sprite.Group()  # particles sprites group
		self.foreground = pygame.sprite.Group()  #  Foreground group
		self.background = pygame.sprite.Group()  # Background sprites group
		self.constraints = pygame.sprite.Group()  # Constraint sprites group

		for layout_name in ["terrain", "foreground", "background"]:
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
			self.projectiles,
			self.game.player_group,
			self.particles,
			self.lights,
			self.foreground,
			self.constraints
		]

		self.calculate_level_size()
		self.level_topleft = self.terrain.sprites()[0].rect
		self.level_bottomright = self.terrain.sprites()[len(self.terrain)-1].rect

	def create_groups(self):
		self.terrain = pygame.sprite.Group()  # Terrain sprites group
		self.lights = pygame.sprite.Group()  # light sprites group
		self.projectiles = pygame.sprite.Group()  # projectiles sprites group
		self.particles = pygame.sprite.Group()  # particles sprites group
		self.foreground = pygame.sprite.Group()  #  Foreground group
		self.background = pygame.sprite.Group()  # Background sprites group
		self.constraints = pygame.sprite.Group()  # Constraint sprites group

		for layout_name in ["terrain", "foreground", "background"]:
			layout = import_csv_layout(self.level_data[layout_name])
			self.create_tile_group(layout, layout_name, 64)

		# light layout
		light_layout = import_csv_layout(self.level_data['torch'])  # Load light layout from CSV
		self.create_tile_group(light_layout, 'light', 64)  # Create light tile sprites

		# Player layout
		player_layout = import_csv_layout(self.level_data['player'])  # Load Player layout from CSV
		self.player_setup(player_layout)  # Set up the Player

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
		tile_list = import_cut_graphics('../assets/terrain/Tileset.png', TILE_SIZE)  # Load tile graphics

		for row_index, row in enumerate(level_data):  # iterate over each row
			for col_index, value in enumerate(row):		# and then over each column
				if value != '-1':  # here we check if a tile should be placed
					x = col_index * tile_size
					y = row_index * tile_size

					# use match case to handle different tile types e.g(foreground/background tiles)
					match tile_type:
						case 'terrain':
							sprite = StaticTile((x, y), [self.terrain], tile_list[int(value)])
						case 'foreground':
							sprite = StaticTile((x, y), [self.foreground], tile_list[int(value)])
						case 'background':
							sprite = StaticTile((x, y), [self.background], tile_list[int(value)])
						case 'light':
							self.light_list.append([[x,y], 100, 30])
							light = StaticTile((x, y), self.lights, tile_list[int(value)])

	def player_setup(self, layout):
		# Set up the player based on the layout
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				if val == '0':
					self.player_spawn = pygame.math.Vector2(x,y)
					self.game.player = Player(self.game, "ALRYN", 96, (x, y), 2, self.game.player_group)

	def respawn(self):
		if self.game.player.rect.bottom >= self.level_height + 300:
			self.game.player.rect.x = self.player_spawn.x
			self.game.player.rect.y = self.player_spawn.y

	""" HANDLERS """
	def light_handler(self):
		for light in self.light_list:
			surf = glow_surface(light[1], [0,50,100], light[2])
			pos = (int((light[0][0] - self.game.camera.level_scroll.x) - light[1]), int((light[0][1] - self.game.camera.level_scroll.y) - light[1]))
			self.game.screen.blit(surf, pos, special_flags=BLEND_RGB_ADD)
			# light.world_light()
			# light.apply_lighting(self.display_surface, light.light_layer, light_source_list=self.lights)
	
	def draw_level(self, surface:pygame.Surface):
		for layer in self.world_layers:			
			for sprite in layer.sprites():
				surface.blit(sprite.image, (sprite.rect.x - self.game.camera.level_scroll.x, sprite.rect.y - self.game.camera.level_scroll.y))

	def update_level(self):
		self.respawn()

	def show_level_markers(self, surface:pygame.Surface, colors:list):
		pygame.draw.rect(surface, colors[0], self.level_topleft)
		pygame.draw.rect(surface, colors[1], self.level_bottomright)


class ParticleSystem2D:
	def __init__(self, game, system_position, N, lifespan, color, size, system_velocity=np.array([0,0]), image=None):
		self.game = game
		self.system_position = system_position
		self.lifespan = lifespan
		self.image = image
		self.color = color
		self.size = size
		self.system_velocity = system_velocity
		self.particles = np.empty(N, dtype=particle_dtype)
		if N != 0:
			self.emit(N, system_position)

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

		# If we still need to emit more particles, append them to the end of the array
		if num_particles > num_reuse:
			new_particles = np.zeros(num_particles - num_reuse, dtype=self.particles.dtype)
			new_particles['position'] = pos
			new_particles['velocity'] = np.random.uniform(-1, 1, (num_particles - num_reuse, 2))
			new_particles['color'] = np.random.uniform(0, 1, (num_particles - num_reuse, 4))
			new_particles['size'] = np.random.uniform(self.size, self.size, num_particles - num_reuse)
			new_particles['lifespan'] = np.random.uniform(self.lifespan, self.lifespan, num_particles - num_reuse)
			self.particles = np.concatenate((self.particles, new_particles))

	def update(self):
		"""
		old_system_position = np.copy(self.system_position)
		#self.system_position = pygame.mouse.get_pos()
		shift = self.system_position - old_system_position
		self.particles['position'] += shift
		"""

		# Update particles position with their velocity
		self.particles['position'] += self.particles['velocity']

		# Then update all particles with system's velocity
		self.particles['position'] += self.system_velocity

		self.particles['lifespan'] -= 1.0

		# Create a mask of "alive" particles
		alive_mask = self.particles['lifespan'] > 0

		# Create a new array of particles that only includes alive particles
		self.particles = self.particles[alive_mask]

	def draw(self):
		for particle in self.particles:
			int_position = [int(x) for x in particle["position"]]
			size = self.size
			pygame.draw.circle(self.game.screen, self.color, int_position, size)
			surf = glow_surface(size*2, (50,50,50), 50)
			offset_pos = (int_position[0] - size*2, int_position[1] - size*2)
			self.game.screen.blit(surf, offset_pos, special_flags=BLEND_RGB_ADD)


class Game():
	def __init__(self):
		self.setup_pygame()
		self.setup_world()
		self.mouse_particles = ParticleSystem2D(self, pygame.mouse.get_pos(), N=50, lifespan=100, color=(60,237,5), size=3)

	def setup_pygame(self):
		self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SCALED)
		self.scaled_display = pygame.Surface((SCREEN_SIZE[0]//3, SCREEN_SIZE[1]//3))
		self.clock = pygame.time.Clock()
		pygame.display.set_caption("ATOT")

	def setup_world(self):
		self.current_level = 2
		self.player_group = pygame.sprite.GroupSingle()
		self.level = Level(self, levels[self.current_level], self.screen)
		self.camera = Camera(self, 20)
		self.world_brightness = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
		self.world_brightness.convert_alpha()
		self.world_brightness.fill([WORLD_BRIGHTNESS, WORLD_BRIGHTNESS, WORLD_BRIGHTNESS])
		self.background_objects = [
			[0.25, [100, 250, 80, 300]],
			[0.25, [380, 120, 80, 100]],
			[0.5, [550, 200, 80, 280]],
		]

	def draw_fps(self):
		fpsCounter = int(self.clock.get_fps())
		draw_text(self.screen, f"FPS: {fpsCounter}", [900, 20])

	def send_frame(self):
		self.clock.tick(FPS)
		self.screen.blit(self.world_brightness, (0,0), special_flags=BLEND_RGB_MULT)
		self.mouse_particles.update()
		self.mouse_particles.emit(1, self.mouse_pos)
		self.mouse_particles.draw()
		self.level.light_handler()
		# self.screen.blit(pygame.transform.scale(self.scaled_display, (SCREEN_SIZE[0], SCREEN_SIZE[1])), (0,0))
		pygame.display.flip()

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
				elif event.key == pygame.K_LSHIFT and self.player.dash_counter > 0:
					self.player.dashing = True
					self.player.dash_counter -= 1

			# key released
			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_LSHIFT:
					self.player.dashing = False

	def update_background(self):
		self.screen.fill([180, 20, 80])
		# self.scaled_display.fill([180, 20, 80])
		for obj in self.background_objects:
			obj_rect = pygame.Rect(
				obj[1][0] - self.camera.level_scroll.x * obj[0], 
				obj[1][1], 
				obj[1][2], 
				obj[1][3]
			)
			if obj[0] == 0.25:
				pygame.draw.rect(self.screen, [0, 0, 125], obj_rect)
			elif obj[0] == 0.5:
				pygame.draw.rect(self.screen, [9, 91, 85], obj_rect)

	def run(self):
		self.running = True
		while self.running:
			self.handle_events()

			for projectile in self.player.projectiles:
				projectile.update(self.camera.level_scroll)

			self.handle_events()
			self.mouse_pos = pygame.mouse.get_pos()
			self.camera.update_position()
			self.update_background()
			self.level.update_level()

			self.level.draw_level(self.screen)
			self.player.update(self.screen, self.level.terrain)
			self.draw_fps()
			self.send_frame()

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