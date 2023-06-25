import random, time
from world_data import worlds
from BLACKFORGE2 import *
from CONSTANTS2 import*


""" SUPPORT FUNCTIONS/CLASSES """
def tile_collision_test(rect:pygame.Rect, tiles:list) -> list:
	""" Returns a list of tiles the given rect is colliding with """
	tiles_collided_with = []

	for tile in tiles:
		for tile_num, tile_rect in enumerate(tile):
			if rect.colliderect(tile[tile_num]):
				tiles_collided_with.append(tile[tile_num])
	
	return tiles_collided_with

def collision_adjust(entity, velocity:pygame.math.Vector2, dt:float, tiles:list):
	collision_types = {
		'top': False,
		'bottom': False,
		'right': False,
		'left': False,
	}

	rect = entity.rect

	# x axis
	rect.x += velocity.x * dt
	tiles_collided_with = tile_collision_test(rect, [tiles])
	for tile in tiles_collided_with:
		if velocity.x > 0:
			rect.right = tile.left
			collision_types['right'] = True
		elif velocity.x < 0:
			rect.left = tile.right
			collision_types['left'] = True
	
	# adjust the entity based on gravity before checking vertical collisions
	entity.physics.apply_gravity(entity, GRAVITY, entity.game.dt)

	# y axis
	rect.y += velocity.y * dt
	tiles_collided_with = tile_collision_test(rect, [tiles])
	for tile in tiles_collided_with:
		if velocity.y <= 0:
			rect.top = tile.bottom
			collision_types['top'] = True
			entity.collide_top = True
		elif velocity.y > 0:
			rect.bottom = tile.top
			collision_types['bottom'] = True
			entity.collide_bottom = True
	
	# check for bumping head
	if collision_types['top'] and velocity.y < 1:
		velocity.y = 0
		
	return rect, collision_types

def glow_surface(radius, color, intensity) -> pygame.Surface:
	intensity = intensity/100
	surface = pygame.Surface((int(radius) * 2, int(radius) * 2), pygame.SRCALPHA)
	surface.convert_alpha()
	pygame.draw.circle(surface, [intensity * value for value in color], (radius, radius), radius)
	surface.set_colorkey([0,0,0])
	return surface

class Particle(pygame.sprite.Sprite):
	def __init__(self, game, color:list, position:tuple, velocity:tuple, radius:int, groups, glow=False, physics=False):
		super().__init__(groups)
		self.game = game
		self.glow = glow
		self.physics = physics
		self.color = color
		self.position = pygame.math.Vector2(position)
		self.velocity = pygame.math.Vector2(velocity)
		self.radius = radius
		self.image = pygame.Surface((self.radius, self.radius))
		self.image.set_colorkey([0,0,0])
		self.rect = pygame.Rect(self.position, (self.radius, self.radius))

	def emit(self):
		# pygame.draw.rect(self.game.screen, "pink", self.rect)
		if self.glow:
			glow = glow_surface(int(self.radius*2), [20,20,20], 100)
			self.game.screen.blit(glow, (self.rect.x - 12, self.rect.y - 4), special_flags=BLEND_RGB_ADD)
		self.position.x += self.velocity.x * self.game.dt
		self.velocity.y += 0.1 * self.game.dt 
		self.position.y += self.velocity.y * self.game.dt
		self.rect.topleft = self.position - self.game.camera.level_scroll
		self.radius -= 0.1

		pygame.draw.circle(self.game.screen, self.color, [int(self.rect.x), int(self.rect.y)], int(self.radius))


""" GAME """
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

	def __init__(self, game, character, size, position, speed, groups):
		super().__init__(size, position, speed, groups)
		# config
		self.game = game
		self.character = character
		self.import_character_assets()
		self.particles = []
		
		self.hurtbox = pygame.Rect( self.rect.topleft, (32,96))

		# player stats
		self.airborne_timer = 0
		self.health = 100
		self.magick = 50
		self.spell_shards = 0
		self.dash_distance = 50
		self.dash_timer = 4
		self.dash_counter = 1
		self.jumps = CHARACTERS[self.character]["JUMPS"]
		self.jump_force = CHARACTERS[self.character]["JUMPFORCE"]

		# stat scales
		self.health_scale = 100
		self.magick_scale = 50
		self.spell_shard_scale = 2

		# player status
		self.status = 'idle'
		self.attacking = False
		self.dashing = False
		self.jumping = False

		# animation
		self.animation = self.animations[self.status]
		self.image = self.animation.animation[0]
		self.attack_duration = 0
		self.rect = pygame.Rect( (self.rect.x, self.rect.y), (32, 96) )

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
			self.animator = Animator(self.game, scaled_images, FRAME_DURATIONS[key], loop)
			self.animations[key] = self.animator

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
		self.jumps -= 1

	def move(self, dt):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_d] and not self.dashing:
			self.facing_right = True
			self.velocity.x = self.speed
		elif keys[pygame.K_a] and not self.dashing:
			self.facing_right = False
			self.velocity.x = -self.speed
		else:
			self.velocity.x = 0

		if keys[pygame.K_LSHIFT] and self.dash_counter > 0:
			self.dash_point = (self.rect.x, self.rect.y)
			self.dashing = True
			self.dash_counter -= 1

		if keys[pygame.K_SPACE] and self.jumps > 0 and self.airborne_timer < 6:
			self.jump(dt)
			self.jumping = True
			self.collide_bottom = False

		# jumps reset
		if self.jumps <= 0 and self.collide_bottom:
			self.jumps = CHARACTERS[self.character]["JUMPS"]

		# attacks
		if self.attacking:
			self.attack()

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
		
		if self.attack_duration >= 5:
			self.attack_duration = 0

		if self.status == 'attack':
			self.attack_duration += 0.2 * self.game.dt
			self.velocity.x = 0
			print(self.attack_duration)
			if int(self.attack_duration) == self.animations[self.status].frame_duration:
				# print(len(self.animations))
				# print("stop attack")
				self.attacking = False
				self.attack_duration = 0
		
	def dash(self, dt):
		frame_scale = self.game.current_fps / 75.0
		adjusted_dash_distance = self.dash_distance * frame_scale

		if self.dashing and self.facing_right and not self.collide_bottom:
			self.velocity.x += adjusted_dash_distance * dt
			marker = pygame.Rect(self.dash_point - self.game.camera.level_scroll, (40,40))
			for i in range(int(self.dash_timer)):
				self.particles.append(Particle(self.game, [255,255,255], self.rect.center, (0, -1), 8, [pygame.sprite.Group()], ))

			pygame.draw.rect(self.game.screen, "white", marker)

		elif self.dashing and not self.facing_right and not self.collide_bottom:
			self.velocity.x += -adjusted_dash_distance * dt
			marker = pygame.Rect(self.dash_point - self.game.camera.level_scroll, (40,40))
			for i in range(int(self.dash_timer)):
				self.particles.append(Particle(self.game, [255,255,255], self.rect.center, (0, -1), 8, [pygame.sprite.Group()], ))
				
			pygame.draw.rect(self.game.screen, "white", marker)

	def get_status(self):
		if self.velocity.y < 0:
			self.status = 'jump'
		elif self.velocity.y > 1:
			self.status = 'fall'
		else:
			if self.velocity.x != 0:
				self.status = 'run'
			elif self.velocity.x < 1:
				self.status = 'idle'
		if self.attacking:
			self.status = 'attack'
	
	def draw(self, surface:pygame.Surface):
		image_offset = ( -30, 0)
		surface.blit(self.image, (self.rect.topleft - self.game.camera.level_scroll + image_offset))

		for particle in self.particles:
			particle.emit()

		# pygame.draw.rect(surface, "white", self.hurtbox)
		# pygame.draw.rect(surface, "white", self.rect)

	def on_screen_check(self):
		if self.rect.x >= self.game.world.level_bottomright.x:
			self.rect.x = self.game.world.level_bottomright.x
		elif self.rect.x <= self.game.world.level_topleft.x:
			self.rect.x = self.game.world.level_topleft.x

	def update(self, dt, surface:pygame.Surface, terrain:pygame.sprite.Group):
		self.move(dt)
		self.dash(dt)
		self.on_screen_check()
		self.get_status()
		self.update_animation()
		
		# update hurtbox
		self.hurtbox.center = self.rect.center - self.game.camera.level_scroll

		# adjust the player based on collisions
		self.rect, self.game.world.collisions = collision_adjust(self, self.velocity, self.game.dt, self.game.world.tile_rects)

		# collision handling
		if self.game.world.collisions['bottom']:
			self.velocity.y = 0
			self.airborne_timer = 0
			self.jumping = False
			self.jumps = CHARACTERS[self.character]["JUMPS"]
		else:
			self.airborne_timer += 1

		# dashing
		if not self.dashing and self.dash_counter <= 0 and self.collide_bottom:
			self.dash_counter = 1

		if self.dashing and self.dash_timer > 0 and not self.collide_bottom:
			self.dash_timer -= 1
			blur_surface = pygame.transform.box_blur(self.image, 4, True)
			self.image = blur_surface

		if self.dash_timer <= 0 or not self.dashing:
			self.dashing = False
			self.dash_timer = 4
		if self.collide_bottom:
			self.dashing = False

		# particles
		for particle in self.particles:
			if particle.radius <= 0:
				self.particles.remove(particle)

		# items
		if self.spell_shards > 2:
			self.spell_shards = 2

		# draw player
		self.draw(surface)

class World():

	def __init__(self, game, world_data):
		# world config
		self.game = game
		self.world_data = world_data
		self.level_topleft = 0
		self.level_bottomright = 0


		# layer setup
		self.create_layer_lists(self.world_data)
		
		# tile setup
		self.tile_index = {}
		self.create_tile_index()
		self.generate_tile_rects()
		self.player_spawn = self.generate_player_spawn(self.world_data)
		
		# world stats
		self.calculate_level_size()
		self.level_topleft = self.tile_rects[0]
		self.level_bottomright = self.tile_rects[len(self.tile_rects)-1]

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
		tile_list = import_cut_graphics('../../assets/terrain/Tileset.png', TILE_SIZE)  # Load tile graphics
		for index, tile in enumerate(tile_list):
			self.tile_index[index] = tile

	def create_layer_lists(self, world_data):
		self.terrain = []
		self.terrain_data = import_csv_layout(world_data['terrain'])
	
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

	def generate_tile_rects(self):
		self.tile_rects = []
		y = 0
		for row in self.terrain_data:
			x = 0
			for tile_num, tile_id in enumerate(row):
				if int(tile_id) != -1 and int(tile_id) in self.tile_index.keys():
					self.tile_rects.append(pygame.Rect( (x * TILE_SIZE, y * TILE_SIZE), ( TILE_SIZE, TILE_SIZE ) ))
				x += 1
			y += 1

	def draw_tiles(self, screen):
		y = 0
		for row in self.terrain_data:
			x = 0
			for tile_num, tile_id in enumerate(row):
				if int(tile_id) != -1 and int(tile_id) in self.tile_index.keys():
					screen.blit(self.tile_index[int(tile_id)], (x * TILE_SIZE - self.game.camera.level_scroll.x, y * TILE_SIZE - self.game.camera.level_scroll.y))
				x += 1
			y += 1

	def respawn(self):
		if self.game.player.rect.bottom >= self.level_height + 300:
			self.game.player.rect.x = self.player_spawn.x
			self.game.player.rect.y = self.player_spawn.y
			self.game.playable = False
		if self.game.player.collide_bottom:
			self.game.playable = True

	def update(self):
		self.respawn()

class UI():
	def __init__(self, game, surface):
		self.game = game
		self.display = surface

		self.player_hud = get_image('../../assets/ui/HUD/HUD.png')
		self.player_hud = scale_images([self.player_hud], (460,100))[0]
	
	def update_player_HUD(self):
		# under bars
		health_under_bar = pygame.Rect((98, 60), (364, 26))
		pygame.draw.rect(self.display, [0,0,0], health_under_bar)
		
		magick_under_bar = pygame.Rect((98, 78), (364, 26))
		pygame.draw.rect(self.display, [0,0,0], magick_under_bar)

		# bars
		health_bar = pygame.Rect((98, 60), (364 * self.game.player.health/self.game.player.health_scale, 26))
		pygame.draw.rect(self.display, [150,0,0], health_bar)
	
		magick_bar = pygame.Rect((90, 90), (374 * self.game.player.magick/self.game.player.magick_scale, 14))
		pygame.draw.rect(self.display, [0,150,200], magick_bar)
		
		self.display.blit(self.player_hud, (5,10))

		if self.game.player.spell_shards > 0:
			spell_shard_1 = pygame.transform.scale(get_image('../../assets/UI/HUD/HUD_SHARD.png'), (54, 30))
			self.display.blit(spell_shard_1, (105, 35))
		
		if self.game.player.spell_shards == 2:
			spell_shard_2 = pygame.transform.scale(get_image('../../assets/UI/HUD/HUD_SHARD.png'), (54, 30))
			self.display.blit(spell_shard_2, (136, 35))
		
class Game():
	def __init__(self):
		self.setup_pygame()
		self.setup_world()

	def setup_pygame(self):
		self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SCALED)
		self.scaled_display = pygame.Surface((SCREEN_SIZE[0]//3, SCREEN_SIZE[1]//3))
		self.clock = pygame.time.Clock()
		pygame.display.set_caption("ATOT")
		# pygame.display.toggle_fullscreen()

	def setup_world(self):
		self.world_brightness = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
		self.world_brightness.convert_alpha()
		self.world_brightness.fill([WORLD_BRIGHTNESS, WORLD_BRIGHTNESS, WORLD_BRIGHTNESS])

		# ui
		self.ui = UI(self, self.screen)

		# create world
		self.current_world = 1
		self.world = World(self, worlds[self.current_world])

		# create player
		self.player_sprite_group = pygame.sprite.GroupSingle()
		self.player = Player(self, "ALRYN", 96, self.world.player_spawn, CHARACTERS["ALRYN"]["SPEED"], [self.player_sprite_group])

		# create camera
		self.camera = Camera(self, 10, 250)
		
		self.background = get_image('../../assets/background.png')
		self.midground = get_image('../../assets/midground.png')
		self.foreground = get_image('../../assets/foreground.png')
		self.full_background = [
			self.background,
			self.midground,
			self.foreground,
		]
		self.full_background = scale_images(self.full_background, (self.world.level_width, self.world.level_height))

	def update_background(self):
		self.screen.fill([55, 55, 92])
		
		self.screen.blit(self.full_background[0], (0,0)-self.camera.level_scroll * 0.25)
		self.screen.blit(self.full_background[1], (0,0)-self.camera.level_scroll * 0.5)
		self.screen.blit(self.full_background[2], (0,0)-self.camera.level_scroll * 0.8)

	def draw_fps(self):
		fpsCounter = int(self.clock.get_fps())
		draw_text(self.screen, f"FPS: {fpsCounter}", [900, 20])

	def send_frame(self):
		self.screen.blit(self.world_brightness, (0,0), special_flags=BLEND_RGB_MULT)
		pygame.display.flip()
		self.clock.tick(FPS)

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
					pass

			# button released
			
			# key pressed
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_f:
					pygame.display.toggle_fullscreen()
				
				# attacking
				if event.key == pygame.K_p and self.player.collide_bottom:
					self.player.attacking = True
				
				# player hud testing
				if event.key == pygame.K_h:
					self.player.health -= 10
				if event.key == pygame.K_m:
					self.player.magick -= 5
				if event.key == pygame.K_s:
					self.player.spell_shards += 1

	def run(self):
		self.running = True
		self.last_time = time.time()
		while self.running:
			self.dt = time.time() - self.last_time  # calculate the time difference
			self.dt *= FPS_SCALE   # scale the dt by the target framerate for consistency
			self.last_time = time.time()  # reset the last_time with the current time
			self.current_fps = self.clock.get_fps()
			
			self.screen.fill([55, 55, 92])

			self.handle_events()

			# updates
			self.world.update()
			self.player.update(self.dt, self.screen, self.world.tile_rects)
			self.camera.update_position()

			# drawing
			self.update_background()
			self.world.draw_tiles(self.screen)
			self.player.draw(self.screen)
			self.ui.update_player_HUD()

			self.mouse_pos = pygame.mouse.get_pos()
			
			self.draw_fps()
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

		# constrain camera velocity
		if self.game.world.level_topleft.left + self.level_scroll.x < 0:
			self.level_scroll.x = 0
		elif self.game.world.level_bottomright.right - self.level_scroll.x < SCREEN_WIDTH:
			self.level_scroll.x = self.game.world.level_width - SCREEN_WIDTH
		
		if self.game.world.level_topleft.top - self.level_scroll.y > 0:
			self.level_scroll.y = 0
		elif self.game.world.level_bottomright.bottom - self.level_scroll.y < SCREEN_HEIGHT:
			self.level_scroll.y = self.game.world.level_height - SCREEN_HEIGHT


if __name__ == "__main__":
	game = Game()
	game.run()