from BLACKFORGE2 import *
from CONSTANTS import *
from entities import *

class World():

	def __init__(self, game, world_data):
		# world config
		self.game = game
		self.world_data = world_data
		self.level_topleft = 0
		self.level_bottomright = 0

		self.constraint_data = None
		self.torch_data = None
		
		# player setup
		self.player_spawn = self.generate_player_spawn(self.world_data)

		# layer setup
		self.create_layer_lists(self.world_data)
		
		# tile setup
		self.tile_index = {}

		self.create_tile_index()
		self.generate_tile_rects()
		self.generate_constraint_rects()
		
		# enemy setup
		self.enemies = []
		self.enemy_spawns = []
		self.enemy_rects = []
		self.generate_enemy_spawns(self.world_data)
		self.spawn_enemies()
		self.generate_enemy_rects()

		# world stats
		self.calculate_level_size()
		self.level_topleft = self.tile_rects[0]
		self.level_bottomright = self.tile_rects[len(self.tile_rects)-1]

		# world fx
		self.num_of_torches = 0
		self.world_particles = []
		self.setup_torches()

		# items
		self.world_items = []

	def calculate_level_size(self):
		max_right = 0
		max_bottom = 0

		for tile in self.tile_rects:
			sprite_rect = tile
			sprite_right = sprite_rect.x + sprite_rect.width
			sprite_bottom = sprite_rect.y + sprite_rect.height

			max_right = max(max_right, sprite_right)
			max_bottom = max(max_bottom, sprite_bottom)
		
		self.level_width = max_right
		self.level_height = max_bottom

	def create_tile_index(self):
		tile_list = import_cut_graphics('../assets/terrain/Tileset.png', TILE_SIZE)  # Load tile graphics
		for index, tile in enumerate(tile_list):
			self.tile_index[index] = tile

	def create_layer_lists(self, world_data):
		self.terrain = []
		self.layer_data = []
		self.background_positions = []
		if 'background' in world_data:
			self.background_data = import_csv_layout(world_data['background'])
			self.layer_data.append(self.background_data)
		else:
			pass
		if 'terrain' in world_data:
			self.terrain_data = import_csv_layout(world_data['terrain'])
			self.layer_data.append(self.terrain_data)
		else:
			pass
		
		self.constraints = []
		if 'constraint' in world_data:
			self.constraint_data = import_csv_layout(world_data['constraint'])
			self.layer_data.append(self.constraint_data)
		else:
			pass
		
		self.torch_positions = []
		if 'torch' in world_data:
			self.torch_data = import_csv_layout(world_data['torch'])
			self.layer_data.append(self.torch_data)
		else:
			pass
		self.foreground_positions = []
		if 'foreground' in world_data:
			self.foreground_data = import_csv_layout(world_data['foreground'])
			self.layer_data.append(self.foreground_data)
		else:
			pass

		self.collision_tile_data = [
			self.terrain_data,
		]
	
	def generate_item_rects(self, world_data):
		pass

	def generate_player_spawn(self, world_data):
		self.player_data = import_csv_layout(world_data['player'])
		y = 0
		for row in self.player_data:
			x = 0
			for index, value in enumerate(row):
				if int(value) == 0:
					self.player_spawn = pygame.math.Vector2(x * TILE_SIZE, y * TILE_SIZE)
				x += 1
			y += 1
		return self.player_spawn
	
	def generate_enemy_spawns(self, world_data):
		self.enemy_data = import_csv_layout(world_data['enemy'])
		y = 0
		for row in self.enemy_data:
			x = 0
			for index, value in enumerate(row):
				if int(value) in [0, 1, 2]:
					self.enemy_spawns.append([pygame.math.Vector2(x * TILE_SIZE, y * TILE_SIZE), int(value)])
				x += 1
			y += 1

	def draw_enemies(self, surface:pygame.Surface):
		for enemy in self.enemies:
			enemy.draw(surface)

	def update_enemies(self, dt, surface:pygame.Surface, terrain:list, constraints:list):
		for enemy in self.enemies:
			enemy.update(terrain, constraints)
		self.despawn_enemy()

	def spawn_enemies(self):
		for spawn in self.enemy_spawns:
			match spawn[1]:
				case 0:
					enemy_name = 'covenant_follower'
				case 1:
					enemy_name = 'rose_sentinel'
				case 2:
					enemy_name = 'sepparition'
			
			self.enemies.append(
				Enemy(self.game, enemy_name, 5, ENEMIES[enemy_name]['SPRITE SIZE'], spawn[0], self.game.enemy_sprites)
			)
			# break
		
	def despawn_enemy(self):
		for enemy in self.enemies:
			if enemy.health <= 0:
				# enemy.status = 'explode'
				enemy.kill()
				self.enemies.remove(enemy)
				if enemy.rect in self.enemy_rects:
					self.enemy_rects.remove(enemy.rect)
				
				# spawn magick_shards on enemy death
				for i in range(enemy.exp):
					position = (
						enemy.rect.x + random.randint(-50, 50), 
						enemy.rect.y + random.randint(-50, 50))
					self.world_items.append(Item(self.game, 
					'magick_shard', 
					'magick', 
					ITEMS['magick']['magick_shard']["SIZE"], 
					position, 
					2, 
					self.game.item_group
						)
					)

					# death particles
					self.world_particles.append(
						Particle(
							self.game,
							[255,255,255],
							enemy.rect.center,
							(random.randint(-5, 5), random.randint(-5, 5)),
							12,
							pygame.sprite.GroupSingle(),
							gravity=True,
							physics=True,
							image_path='../assets/items/magick/magick_shard/magick_shard1.png'
						)
					)
		
	def generate_enemy_rects(self):
		for enemy in self.enemies:
			self.enemy_rects.append(enemy.rect)

	def generate_tile_rects(self):
		self.tile_rects = []
		for layer in self.collision_tile_data:
			y = 0
			for row in layer:
				x = 0
				for tile_num, tile_id in enumerate(row):
					if int(tile_id) != -1 and int(tile_id) in self.tile_index.keys() and int(tile_id) not in [18]:
						self.tile_rects.append(pygame.Rect( (x * TILE_SIZE, y * TILE_SIZE), ( TILE_SIZE, TILE_SIZE ) ))
					x += 1
				y += 1
	
	def generate_constraint_rects(self):
		self.constraint_rects = []
		y = 0
		if self.constraint_data:
			for row in self.constraint_data:
				x = 0
				for tile_num, tile_id in enumerate(row):
					if int(tile_id) != -1 and int(tile_id) in self.tile_index.keys():
						self.constraint_rects.append(pygame.Rect( (x * TILE_SIZE, y * TILE_SIZE), ( TILE_SIZE, TILE_SIZE ) ))
					x += 1
				y += 1

	def setup_torches(self):
		# torches
		y = 0
		for row in self.torch_data:
			x = 0
			for tile_num, tile_id in enumerate(row):
				if int(tile_id) == 18:
					self.num_of_torches += 1
				x += 1
			y += 1
					
	def generate_torch_positions(self):
		y = 0
		if self.torch_data:
			for row in self.torch_data:
				x = 0
				for tile_num, tile_id in enumerate(row):
					if int(tile_id) == 18:
						self.torch_positions.append([pygame.math.Vector2(x * TILE_SIZE - self.game.camera.level_scroll.x, y * TILE_SIZE - self.game.camera.level_scroll.y)])
						if len(self.torch_positions) > self.num_of_torches:
							self.torch_positions.pop(self.num_of_torches)
					else:
						pass
					x += 1
				y += 1

	def draw_tiles(self, screen):
		for layer in self.layer_data:
			y = 0
			for row in layer:
				x = 0
				for tile_num, tile_id in enumerate(row):
					if int(tile_id) != -1 and int(tile_id) in self.tile_index.keys():
						screen.blit(self.tile_index[int(tile_id)], (x * TILE_SIZE - self.game.camera.level_scroll.x, y * TILE_SIZE - self.game.camera.level_scroll.y))
					x += 1
				y += 1

	def respawn(self):
		if self.game.player.health <= 0:
			self.game.player.rect.x = self.player_spawn.x
			self.game.player.rect.y = self.player_spawn.y
			self.game.player.health = CHARACTERS[self.game.player.character]["HEALTH"]
		else:
			if self.game.player.rect.bottom >= self.level_height + 300:
				self.game.player.rect.x = self.player_spawn.x
				self.game.player.rect.y = self.player_spawn.y
				self.game.player.health = CHARACTERS[self.game.player.character]["HEALTH"]
				self.game.player.magick = CHARACTERS[self.game.player.character]["MAGICK"]
				self.game.playable = False
			if self.game.player.collide_bottom:
				self.game.playable = True

	def world_FX(self):
		# world particles
		for index, pos in enumerate(self.torch_positions):
			for x in range(6):
				self.world_particles.append(
					Particle(
						self.game, 
						random.choice(seto_colors["torch1"]), 
						((int(self.torch_positions[index][0].x) + 28) + random.randint(-10, 10), int(self.torch_positions[index][0].y) + 32),
						(0, random.randint(-3,-1)), 
						random.randint(2,8), 
						[], 
						torch=True,
						)
				)
		
		# world lights
		for index, position in enumerate(self.torch_positions):
			torch_glow = glow_surface(TILE_SIZE*2, [20,20,40],120)
			self.game.world_brightness.blit(torch_glow, (position[0].x, (position[0].y + 32)) - self.game.camera.level_scroll - (102, 122), special_flags=pygame.BLEND_RGB_ADD)

		# player spell FX
		for spell in self.game.player.projectiles:
			if spell.status not in ['hit', 'remove']:
				spell_glow = glow_surface(spell.size.x, [20,20,20], 100)
				self.game.world_brightness.blit(spell_glow, spell.rect.topleft - self.game.camera.level_scroll - (30, 30), special_flags=BLEND_RGB_ADD)

		# enemy FX
		for enemy in self.enemies:
			for spell in enemy.spells:
				# spell lights
				if spell.status not in ['hit', 'remove']:
					spell_glow = glow_surface(spell.size.x, [20,20,20], 100)
					self.game.world_brightness.blit(spell_glow, spell.rect.topleft - self.game.camera.level_scroll - (50, 50), special_flags=BLEND_RGB_ADD)

	def update_FX(self, surface:pygame.Surface):
		for particle in self.world_particles:
			particle.emit()
			if particle.radius <= 0.5:
				self.world_particles.remove(particle)

	def update_items(self, surface:pygame.Surface):
		for item in self.world_items:
			item.status = 'active'
			item.update(surface)

			if item.status in ['collected', 'despawned']:
				self.world_items.remove(item)

	def draw_map_image(self, surface:pygame.Surface):
		map_image = get_image(f'../levels/level_data/{world_names[self.game.current_world]}.png')
		map_image = scale_images([map_image], (self.level_width, self.level_height))[0]
		surface.blit(map_image, (0,0) - self.game.camera.level_scroll)

	def draw_world(self, surface:pygame.Surface):
		# self.spawn_enemies()
		# draw tiles
		# self.draw_map_image(surface)
		self.draw_tiles(surface)
		self.generate_torch_positions()
		self.update_FX(surface)
		# draw player????
		self.game.player.draw(surface)
		# draw enemies
		self.draw_enemies(surface)
		# draw vfx
		self.world_FX()

	def update(self):
		self.respawn()
