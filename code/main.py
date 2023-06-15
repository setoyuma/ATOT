from BLACKFORGE2 import *

import random
from CONSTANTS import*
from game_data import levels
from particle import Particle
from projectile import Projectile

class Camera():
	def __init__(self, game, interpolation:int):
		self.game = game
		self.player = self.game.player
		self.level_scroll = pygame.math.Vector2()
		self.interpolation = interpolation

	def horizontal_scroll(self):
		self.level_scroll.x += (self.player.rect.centerx - self.level_scroll.x - (SCREEN_SIZE[0]//2 - self.player.size.x)) / self.interpolation

	def vertical_scroll(self):
		self.level_scroll.y += ((self.player.rect.centery - 80) - self.level_scroll.y - (SCREEN_SIZE[1]//2 - self.player.size.y)) / self.interpolation

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
		self.rect = self.image.get_rect(topleft = position)
		self.projectiles = []

		# player stats
		self.dash_timer = 10
		self.dash_counter = 1
		self.jump_force = CHARACTERS[self.character]["JUMPFORCE"]

		# player status
		self.status = 'idle'
		self.attacking = False
		self.dashing = False

	""" PLAYER ASSETS """
	def import_character_assets(self):
		character_path = '../assets/character/'
		self.animations = {'idle':[],'run':[],'jump':[],'fall':[]}

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
			# self.image = image
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
			self.velocity.x += 5.3
		elif self.dashing and not self.facing_right and not self.collide_bottom:
			self.velocity.x -= 5.3

	def attack(self):
		if self.facing_right:
			hitbox = pygame.Rect(
				(
				(self.rect.x + 40) - self.game.camera.level_scroll.x, 
				(self.rect.y + 25) - self.game.camera.level_scroll.y
				), 
				(60, 40)
				)
		elif not self.facing_right:
			hitbox = pygame.Rect(
				(
				(self.rect.x - 13) - self.game.camera.level_scroll.x, 
				(self.rect.y + 25) - self.game.camera.level_scroll.y
				), 
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
		# self.draw(surface)
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
			# print("dash timer reset")
			self.dashing = False
			self.dash_timer = 10

class Level():
	def __init__(self, game, level_data, surface):
		self.game = game
		self.level_data = level_data
		self.display_surface = surface

		# Lighting
		self.light_list = []

		# particles
		self.particles = []

		self.terrain = pygame.sprite.Group()  # Terrain sprites group
		self.lights = pygame.sprite.Group()  # light sprites group
		self.projectiles = pygame.sprite.Group()  # projectiles sprites group
		self.foreground = pygame.sprite.Group()  #  Foreground group
		self.background = pygame.sprite.Group()  # Background sprites group
		self.constraints = pygame.sprite.Group()  # Constraint sprites group

		# Terrain layout
		terrain_layout = import_csv_layout(self.level_data['terrain'])
		self.create_tile_group(terrain_layout, 'terrain', 64)

		# light layout
		light_layout = import_csv_layout(level_data['torch'])  # Load light layout from CSV
		self.create_tile_group(light_layout, 'light', 64)  # Create light tile sprites
		
		# Foreground layout
		foreground_layout = import_csv_layout(level_data['foreground'])  # Load Foreground layout from CSV
		self.create_tile_group(foreground_layout, 'foreground', 64)  # Create Foreground tile sprites
		
		# Background layout
		background_layout = import_csv_layout(level_data['background'])  # Load Background layout from CSV
		self.create_tile_group(background_layout, 'background', 64)  # Create Background tile sprites

		# Player layout
		player_layout = import_csv_layout(level_data['player'])  # Load Player layout from CSV
		self.player_setup(player_layout)  # Set up the Player

		self.world_layers = [
			self.background,
			self.terrain,
			self.lights,
			self.projectiles,
			self.game.player_sprite_group,
			self.foreground,
			self.constraints,
		]

		self.calculate_level_size()

		self.level_topleft = self.terrain.sprites()[0].rect
		self.level_bottomright = self.terrain.sprites()[len(self.terrain)-1].rect

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
						# case 'light':
						# 	self.light_list.append(Light(50, "teal", 15, SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_BRIGHTNESS))
						# 	light = StaticTile((x, y), self.lightes, tile_list[int(value)])

	def player_setup(self, layout):
		# Set up the player based on the layout
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * TILE_SIZE
				y = row_index * TILE_SIZE
				if val == '0':
					self.game.player = Player(self.game, "ALRYN", 96, (x, y), 2, self.game.player_sprite_group)

	""" HANDLERS """
	def light_handler(self):
		for light in self.light_list:
			light.world_light()
			light.apply_lighting(self.display_surface, light.light_layer, light_source_list=self.lightes)
			break
	
	def particle_handler(self):
		# Handle the particles in the level
		# light particles

		for light in self.lights.sprites():
			self.particles.append(Particle(light.rect.centerx, light.rect.centery, '', 3, [0,255,255], 'light'))

		# Draw and update particles
		for particle in self.particles:
			particle.update(self.camera)
			particle.draw(self.display_surface, self.camera)

		self.particles = [particle for particle in self.particles if not particle.is_expired()]

	def draw_level(self, surface:pygame.Surface):
		for layer in self.world_layers:			
			for sprite in layer.sprites():
				surface.blit(sprite.image, (sprite.rect.x - self.game.camera.level_scroll.x, sprite.rect.y - self.game.camera.level_scroll.y))

	def update_level(self):
		self.light_handler()
		self.particle_handler()

	def show_level_markers(self, surface:pygame.Surface, colors:list):
		pygame.draw.rect(surface, colors[0], self.level_topleft)
		pygame.draw.rect(surface, colors[1], self.level_bottomright)

class Game():
	def __init__(self):
		self.screen = pygame.display.set_mode(SCREEN_SIZE)
		self.scaled_display = pygame.Surface((SCREEN_SIZE[0]//3, SCREEN_SIZE[1]//3))
		pygame.display.set_caption("Example")
		self.clock = pygame.time.Clock()
		self.player_sprite_group = pygame.sprite.GroupSingle()

		self.current_level = 2
		self.level = Level(self, levels[self.current_level], self.screen)

		# camera
		self.camera = Camera(self, 20)

		self.background_objects = [
			[
				0.25,
				[100, 250, 80, 300]
			],
			[
				0.25,
				[380, 120, 80, 100]
			],
			[
				0.5,
				[550, 200, 80, 280]
			],
		]

		self.particles = []

	def draw_fps(self):
		fpsCounter = int(self.clock.get_fps())
		draw_text(self.screen, f"FPS: {fpsCounter}", [900, 20])

	""" Main Game Loop """
	def handle_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 4:  # Mouse wheel up
					pass
				if event.button == 5:  # Mouse wheel down
					pass
				if event.button == 1:
					self.player.attacking = True
			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					self.player.attacking = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_f:
					pygame.display.toggle_fullscreen()
				if event.key == pygame.K_LSHIFT and self.player.dash_counter > 0:
					self.player.dashing = True
					self.player.dash_counter -= 1
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LSHIFT:
					self.player.dashing = False

	def glow_surface(self, radius, color):
		surface = pygame.Surface((radius * 2, radius * 2))
		pygame.draw.circle(surface, color, (radius, radius), radius)
		surface.set_colorkey([0,0,0])
		return surface

	def run(self):
		self.running = True
		while self.running:
			self.screen.fill([180, 20, 80])
			# self.scaled_display.fill([180, 20, 80])

			for object in self.background_objects:
				object_rect = pygame.Rect(
					object[1][0] - self.camera.level_scroll.x * object[0], 
					object[1][1], 
					object[1][2], 
					object[1][3]
				)
				if object[0] == 0.25:
					pygame.draw.rect(self.screen, [0, 0, 125], object_rect)
				elif object[0] == 0.5:
					pygame.draw.rect(self.screen, [9, 91, 85], object_rect)

			mx, my = pygame.mouse.get_pos()
			self.particles.append(
				[[mx, my], [random.randint(0,20) / 10 - 1, -2], random.randint(6,12)]
			)

			for particle in self.particles:
				particle[0][0] += particle[1][0]
				particle[0][1] += particle[1][1]
				particle[2] -= 0.1
				particle[1][1] += 0.2
				pygame.draw.circle(self.screen, "white", [int(particle[0][0]), int(particle[0][1])], int(particle[2]))
				if particle[2] <= 0:
					self.particles.remove(particle)

				glow_radius = particle[2] * 2
				self.screen.blit(self.glow_surface(glow_radius, [20,20,20]), (int(particle[0][0] - glow_radius), int(particle[0][1] - glow_radius)), special_flags=BLEND_RGB_ADD)


			self.handle_events()

			for projectile in self.player.projectiles:
				projectile.update(self.camera.level_scroll)

			print(self.player.dash_counter)

			self.camera.update_position()
			self.level.draw_level(self.screen)
			self.level.update_level()
			self.player.update(self.screen, self.level.terrain)
			self.draw_fps()
			self.clock.tick(FPS)
			# self.screen.blit(pygame.transform.scale(self.scaled_display, (SCREEN_SIZE[0], SCREEN_SIZE[1])), (0,0))
			pygame.display.flip()

if __name__ == "__main__":
	game = Game()
	game.run()