import random, time
from world_data import worlds
from BLACKFORGE2 import *
from CONSTANTS2 import*

def tile_collision_test(rect:pygame.Rect, tiles:list) -> list:
	""" Returns a list of tiles the given rect is colliding with """
	tiles_collided_with = []

	for tile in tiles:
		for tile_num, tile_rect in enumerate(tile):
			if rect.colliderect(tile[tile_num]):
				tiles_collided_with.append(tile[tile_num])
	
	return tiles_collided_with

def collision_adjust(entity, dt:float, collision_tiles:list, gravity_value:float):
	collision_types = {
		'top': False,
		'bottom': False,
		'right': False,
		'left': False,
	}

	rect = entity.rect
	velocity = entity.velocity
	position = entity.position
 
	# x axis
	position.x += velocity.x * dt
	rect.center = position
	tiles_collided_with = tile_collision_test(rect, [collision_tiles])
	for tile in tiles_collided_with:
		if velocity.x > 0:
			rect.right = tile.left
			collision_types['right'] = True
		elif velocity.x < 0:
			rect.left = tile.right
			collision_types['left'] = True
	
	# adjust the entity based on gravity before checking vertical collisions
	entity.physics.apply_gravity(entity, gravity_value, dt)

	# y axis
	position.y += velocity.y * dt
	rect.center = position
	tiles_collided_with = tile_collision_test(rect, [collision_tiles])
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



class Player(Entity):
	def __init__(self, game, character, size, position, speed, groups):
		super().__init__(size, position, speed, groups)
		self.game = game
		self.character = character
		self.import_character_assets()

		""" PLAYER STATS """
		# player stats
		self.jumps = CHARACTERS[self.character]["JUMPS"]
		self.jump_force = CHARACTERS[self.character]["JUMPFORCE"]

		# player status
		self.status = 'idle'
		self.attacking = False
		self.dashing = False
		self.rolling = False
		self.jumping = False

		# animation
		self.animation = self.animations[self.status]
		self.image = self.animation.animation[0]
		self.attack_duration = 0
		self.rect = pygame.Rect( (self.rect.x, self.rect.y), (32, 96) )
		self.hurtbox = pygame.Rect( self.rect.topleft, (self.rect.width/2, self.rect.height) )

	""" ANIMATIONS """
	def import_character_assets(self):
		self.animations = {}
		self.animation_keys = {'idle':[],'run':[],'jump':[],'fall':[], 'attack':[],} 
		for key in self.animation_keys:
			full_path = CHAR_PATH + key
			original_images = import_folder(full_path)
			scaled_images = scale_images(original_images, self.size)
			loop = False
			self.animator = Animator(self.game, scaled_images, FRAME_DURATIONS[key], loop)
			self.animations[key] = self.animator

	def update_animation(self):
		self.animation = self.animations[self.status]
		if self.animation.done and not self.animation.loop:
			if self.status in self.animation_keys:
				self.status = "idle"
				self.animation.reset()

		if self.facing_right:
			flipped_image = pygame.transform.flip(self.animation.update(self.game.dt), False, False)
			self.image = flipped_image
		else:
			flipped_image = pygame.transform.flip(self.animation.update(self.game.dt), True, False)
			self.image = flipped_image

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
		
		if self.rolling:
			self.status = 'roll'

	""" MOVEMENT """
	def move(self, dt):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_a]:
			self.velocity.x = -1 * self.speed * dt
			self.facing_right = False
		elif keys[pygame.K_d]:
			self.velocity.x = 1 * self.speed * dt
			self.facing_right = True
		else:
			self.velocity.x = 0

		if keys[pygame.K_SPACE]:
			self.jump(dt)

	def jump(self, dt):
		self.jumping = True
		self.velocity.y = -self.jump_force * dt

	""" UPDATE """
	def draw(self, surface:pygame.Surface):
		surface.blit(self.image, (self.rect.topleft))
		# surface.blit(self.image, (self.rect.topleft - self.game.camera.level_scroll))
	
	def update(self, dt):
		self.move(dt)

		# self.position.x += self.velocity.x * dt
		# self.position.y += self.velocity.y * dt
		
		# adjust the player based on collisions
		terrain = [
			pygame.Rect((300,300), (64,64)),
			]
		self.rect, collisions = collision_adjust(self, self.game.dt, terrain, GRAVITY)
		
		self.hurtbox.center = self.rect.center

		for t in terrain:
			terrain_surf = pygame.Surface(t.size)
			terrain_surf.fill([0,0,255])
			self.game.screen.blit(terrain_surf, t.center)

		pygame.draw.rect(self.game.screen, "pink", self.hurtbox)

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
		# create world

		# create player
		self.player_group = pygame.sprite.Group()
		self.player = Player(self, 'ALRYN', 96, (150,150), 4, [self.player_group])
		# create camera
		# self.camera = Camera(self, 10, 250)

		pass
		
	def update_background(self):
		self.screen.fill([55, 55, 92])

	def draw_fps(self):
		fpsCounter = int(self.clock.get_fps())
		draw_text(self.screen, f"FPS: {fpsCounter}", [900, 20])

	def send_frame(self):
		pygame.display.flip()
		self.clock.tick(FPS)

	def handle_events(self):
		for event in pygame.event.get():
			# quit
			if event.type == pygame.QUIT:
				self.running = False
			
			# key pressed
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_f:
					pygame.display.toggle_fullscreen()

	def run(self):
		self.running = True
		self.last_time = time.time()
		while self.running:
			self.dt = time.time() - self.last_time  # calculate the time difference
			self.dt *= FPS_SCALE   # scale the dt by the target framerate for consistency
			self.last_time = time.time()  # reset the last_time with the current time
			self.current_fps = self.clock.get_fps()
			
			# self.screen.fill([55, 55, 92])

			self.handle_events()
			self.update_background()

			self.player.update(self.dt)

			self.player.draw(self.screen)

			self.draw_fps()
			self.send_frame()

			# print(len(self.world.constraint_rects))

class Camera():
    
	def __init__(self, game, player, scroll_speed:int, interpolation:int):
		self.game = game
		self.player = self.game.player
		self.level_scroll = pygame.math.Vector2()
		self.scroll_speed = scroll_speed
		self.interpolation = interpolation

	def horizontal_scroll(self):
		self.level_scroll.x += (
			(
				self.player.rect.centerx - self.level_scroll.x - (HALF_WIDTH - self.player.size.x)
			) / self.interpolation * self.scroll_speed
			)

	def vertical_scroll(self):
		self.level_scroll.y += (
			(
				(self.player.rect.centery - 50) - self.level_scroll.y - (HALF_HEIGHT - self.player.size.y)
			) / self.interpolation * self.scroll_speed
			)

	def update_position(self, level_topleft_rect:pygame.Rect, level_bottomright_rect:pygame.Rect, level_width:int, level_height:int, SCREEN_WIDTH:int, SCREEN_HEIGHT:int):
		self.horizontal_scroll()
		self.vertical_scroll()

		# constrain camera movement
		if level_topleft_rect.left + self.level_scroll.x < 0:
			self.level_scroll.x = 0
		elif level_bottomright_rect.right - self.level_scroll.x < SCREEN_WIDTH:
			self.level_scroll.x = level_width - SCREEN_WIDTH

		if level_topleft_rect.top - self.level_scroll.y > 0:
			self.level_scroll.y = 0
		elif level_bottomright_rect.bottom - self.level_scroll.y < SCREEN_HEIGHT:
			self.level_scroll.y = level_height - SCREEN_HEIGHT


if __name__ == '__main__':
	game = Game()
	game.run()