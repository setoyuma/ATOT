import random, time
from math import sin
from world_data import worlds
from BLACKFORGE2 import *
from CONSTANTS import *


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

def sine_wave_value() -> int:
	value = sin(pygame.time.get_ticks())
	if value >= 0: 
		return 255
	else: 
		return 0

class Item(Entity):

	def __init__(self, game, item_name, type, size, position, speed, groups):
		super().__init__(size, position, speed, groups)
		self.game = game
		self.type = type
		self.item_name = item_name
		self.import_assets()
		self.get_stats()

		# item status
		self.status = 'inactive'

		# animation
		self.frame_index = 0
		self.animation = self.animation_keys[self.item_name]

	def get_stats(self):
		self.stats = ITEMS[self.type][self.item_name]
		self.name = self.stats['NAME']
		self.animation_speed = self.stats['ANIM SPEED']
		self.recovery = self.stats['RECOV']
		self.pickup_radius = self.stats['PICKUP_RAD']
		self.timer = self.stats['TIME']
		self.size = pygame.math.Vector2(self.stats['SIZE'], self.stats['SIZE'])

	def import_assets(self):
		if self.type == 'magick' and 'shard' in self.item_name:
			self.animation_keys = {'magick_shard':[]} 

		for animation in self.animation_keys:
			full_path = ITEMS_PATH + self.type + '/' + animation
			original_images = import_folder(full_path)
			scaled_images = scale_images(original_images, self.size)
			
			self.animation_keys[animation] = import_folder(full_path)
		self.animations = self.animation_keys
	
	def animate(self):
		animation = self.animation_keys[self.item_name]
		self.frame_index += self.animation_speed * self.game.dt
		if self.frame_index >= len(animation):
			self.frame_index = 0
			self.image = pygame.transform.scale(animation[int(self.frame_index)], self.size)
		elif self.status == 'decay':
			self.image.set_alpha(sine_wave_value())
		else:
			self.image = pygame.transform.scale(animation[int(self.frame_index)], self.size)

	def draw(self, surface:pygame.Surface):
		surface.blit(self.image, self.rect.topleft - self.game.camera.level_scroll)

	def get_player_distance_direction(self, player):
		enemy_vec = pygame.math.Vector2(self.rect.center)
		player_vec = pygame.math.Vector2(player.rect.center)
		distance = (player_vec - enemy_vec).magnitude()
		
		self.pickup_radius_rect = pygame.Rect(self.rect.topleft, (self.pickup_radius, self.pickup_radius))


		if self.game.player.rect.colliderect(self.pickup_radius_rect) and distance > 0:
			direction = (player_vec - enemy_vec).normalize()
		else:
			direction = pygame.math.Vector2()

		return (distance,direction)
	
	def actions(self, player):
		if self.status == 'inactive':
			self.direction = pygame.math.Vector2()
		elif self.status == 'active':
			self.direction = self.get_player_distance_direction(player)[1]
		else:
			self.direction = pygame.math.Vector2()

		if self.direction.x > 0:
			self.direction_facing = 'right'
		elif self.direction.x < 0:
			self.direction_facing = 'left'

	def move(self):
		match self.type:
			case 'magick':
				if self.direction.magnitude() != 0:
					self.direction = self.direction.normalize()

				self.velocity.x = self.direction.x * self.speed * self.game.dt

	def get_status(self, surface:pygame.Surface):
		if self.status == 'inactive':
			pass
		elif self.status == 'collected':
			self.kill()

	def get_pickup_status(self):
		if self.game.player.rect.colliderect(self.rect):
			self.status = 'collected'

			match self.type:
				case 'magick':
					self.game.player.magick += self.recovery
					if 'shard' in self.item_name:
						self.game.player.current_spell_shard_count += 1
					# print('player gained', self.recovery, 'magick')

					for spell in self.game.player.projectiles:
						if spell.rect.colliderect(self.rect):
							pass

	def update(self, surface:pygame.Surface):
		if self.status not in ['collected', 'inactive']:
			self.timer -= 0.1 * self.game.dt
			if self.timer <= self.stats['TIME'] - 12:
				self.status = 'decay'
			if self.timer <= 0:
				self.status = 'despawned'
				self.timer = self.stats['TIME']
			
			self.actions(self.game.player)
			self.animate()
			self.get_status(surface)
			self.get_pickup_status()
			self.draw(surface)

			self.rect, self.game.world.collisions = collision_adjust(self, self.velocity, self.game.dt, self.game.world.tile_rects)
			# collision handling
			if self.game.world.collisions['bottom']:
				self.velocity.y = 0
			
			self.move()

class Particle(pygame.sprite.Sprite):
	
	def __init__(self, game, color:list, position:tuple, velocity:tuple, radius:int, groups, glow=False, gravity=False, torch=False):
		# super().__init__(groups)
		self.game = game
		self.glow = glow
		self.torch = torch
		self.gravity = gravity
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
			self.game.screen.blit(glow, (self.rect.x - 4, self.rect.y + 3), special_flags=BLEND_RGB_ADD)
		if self.torch:
			self.velocity.x = 0.1
			# self.velocity.y = -float(random.randint(1, 10)) * self.game.dt
			self.position.x += self.velocity.x * self.game.dt
		else:
			self.position.x += self.velocity.x * self.game.dt
		if self.gravity:
			self.velocity.y += 0.2 * self.game.dt 
		self.position.y += self.velocity.y * self.game.dt
		self.rect.topleft = self.position - self.game.camera.level_scroll
		self.radius -= 0.1 * self.game.dt

		pygame.draw.circle(self.game.screen, self.color, [int(self.rect.x), int(self.rect.y)], int(self.radius))

class Projectile(pygame.sprite.Sprite):
	
	def __init__(self, game, position:tuple, projectile_type:str, direction:str, cast_from:tuple, dist:int):
		super().__init__()
		self.game = game
		self.position = pygame.math.Vector2(position)
		self.projectile_type = projectile_type
		self.size = pygame.math.Vector2(SPELLS[self.projectile_type][0], SPELLS[self.projectile_type][0])
		self.speed = SPELLS[self.projectile_type][1]
		self.damage = SPELLS[self.projectile_type][2]
		self.direction = direction
		self.distance = dist
		self.cast_from = pygame.math.Vector2(cast_from)
		
		# status
		self.status = 'cast'
		self.collided = False

		# animation
		self.frame_index = 0
		self.import_assets()
		self.animation = self.animation_keys[self.projectile_type]
		# self.image = self.animation[0]
		self.animation_speed = 0.25
		self.rect = pygame.Rect(self.position, self.size)

	def import_assets(self):
		self.animation_keys = {'fireball':[],'windblade':[], 'wind_sparks':[], 'fire_sparks':[]} 

		for animation in self.animation_keys:
			full_path = SPELL_PATH + animation
			
			original_images = import_folder(full_path)
			scaled_images = scale_images(original_images, self.size)
			
			self.animation_keys[animation] = import_folder(full_path)
		self.animations = self.animation_keys
	
	def animate(self):
		animation = self.animation_keys[self.projectile_type]
		self.frame_index += self.animation_speed * self.game.dt
		if self.frame_index >= len(animation):
			self.frame_index = 0
		if self.direction == 'right':
			self.image = pygame.transform.scale(animation[int(self.frame_index)], self.size)
		if self.direction == 'left':
			self.image = pygame.transform.flip(pygame.transform.scale(animation[int(self.frame_index)], self.size), True, False)

	def check_collision(self, collideables:list):
		for object_list in collideables:
			for obj in object_list:
				if self.rect.colliderect(obj):
					self.collided = True
					
	def create_hitspark_animation(self):
		hitspark_images = []  # Placeholder list for demonstration
		hitspark_pos = self.rect.center
		# Create hitspark animation using hitspark_images and hitspark_pos
		# ...
	
	def draw(self, surface:pygame.Surface):
		surface.blit(self.image, self.rect.topleft - self.game.camera.level_scroll)
		# pygame.draw.rect(self.game.screen, [0,255,0], self.rect )
		# pygame.draw.rect(self.game.screen, [0,255,0], self.hitbox )

	def handle_status(self):
		if self.status == 'hit' or self.collided:
			match self.projectile_type:
				case 'windblade':
					self.projectile_type = 'wind_sparks'
				case 'fireball':
					self.projectile_type = 'fire_sparks'
		
			if self.frame_index + 1 >= len(self.animations[self.projectile_type]):
				self.status = 'remove'

	def update(self):
		self.handle_status()
		self.animate()
		match self.direction:
			case 'right':
				if self.status not in ['hit', 'remove'] and not self.collided:
					self.position.x += self.speed * self.game.dt
			case 'left':
				if self.status not in ['hit', 'remove'] and not self.collided:
					self.position.x += -self.speed * self.game.dt

		self.rect.center = self.position
		self.check_collision([self.game.world.tile_rects, self.game.world.enemy_rects])

""" GAME """
class Weapon(pygame.sprite.Sprite):
	def __init__(self,game,player,groups):
		super().__init__(groups)
		self.game = game
		direction = player.status.split('_')[0]

		# graphic
		full_path = f'../assets/weapons/{player.current_weapon}/{player.current_weapon}.png'
		self.image = get_image(full_path).convert_alpha()
		self.image = scale_images([self.image], (32, 32))
		self.image = self.image[0]

		# placement
		if player.facing_right:
			self.hitbox = self.image.get_rect(midleft = player.rect.midright + pygame.math.Vector2(0,-26))
			self.rect = self.image.get_rect(midleft = player.rect.midright + pygame.math.Vector2(0,-26))
			self.hitbox.width = TILE_SIZE
		elif not player.facing_right:
			self.image = pygame.transform.flip(self.image, True, False)
			self.hitbox = self.image.get_rect(midleft = player.rect.midright + pygame.math.Vector2(-26,-26))
			self.rect = self.image.get_rect(midright = player.rect.midleft + pygame.math.Vector2(-26,-26))
			self.hitbox.width = TILE_SIZE

	def draw(self, surface:pygame.Surface):
		self.hitbox.topleft = self.rect.topleft - self.game.camera.level_scroll
		surface.blit(self.image, self.rect.center - self.game.camera.level_scroll)
		# pygame.draw.rect(self.game.screen, "white", self.hitbox)
		# pygame.draw.rect(self.game.screen, "white", self.rect)

class Enemy(Entity):
	
	def __init__(self, game, enemy_name, speed, size, position, groups):
		super().__init__(size, position, speed, groups)
		self.game = game
		self.grab_stats(enemy_name)
		self.import_assets(enemy_name)

		self.directions = [
			'left',
			'right',
		]
		self.direction_facing = random.choice(self.directions)
		self.patrol_timer = 0
		
		# status
		self.vulnerable = True
		self.can_attack = True
		self.aggro_rect = pygame.Rect(self.rect.topleft, (self.aggro_range, self.aggro_range))


		# animation
		self.status = 'move'
		self.frame_index = 0
		self.animation = self.animation_keys[self.status]
		self.animation_speed = 0.25

	def grab_stats(self, enemy_name):
		self.stats = ENEMIES[enemy_name]
		self.name = self.stats['NAME']
		self.health = self.stats['HEALTH']
		self.exp = self.stats['EXP']
		self.damage = self.stats['DAMAGE']
		self.attack_type = self.stats['ATTACK_TYPE']
		self.speed = self.stats['SPEED']
		self.resistance = self.stats['RESIST']
		self.attack_cooldown = self.stats['ATK_CD']
		self.invincibility_duration = self.stats['IFRAMES']
		self.attack_radius = self.stats['ATK_RAD']
		self.aggro_range = self.stats['AGR_RNG']
		self.attacks = self.stats['ATTACKS']
		self.gravity = self.stats['GRAVITY']

	def import_assets(self, enemy_name):
		self.animation_keys = {'move':[],'attack':[]} 

		for animation in self.animation_keys:
			full_path = ENEMY_PATH + enemy_name + '/' + animation
			
			original_images = import_folder(full_path)
			scaled_images = scale_images(original_images, self.size)
			
			self.animation_keys[animation] = import_folder(full_path)

		self.animations = self.animation_keys
	
	def animate(self):
		animation = self.animation_keys[self.status]
		self.frame_index += self.animation_speed * self.game.dt
		if self.frame_index >= len(animation):
			self.frame_index = 0
			if self.status == 'attack':
				self.can_attack = False
		if self.direction_facing == 'right':
			self.image = pygame.transform.flip(pygame.transform.scale(animation[int(self.frame_index)], self.size), True, False)
		if self.direction_facing == 'left':
			self.image = pygame.transform.scale(animation[int(self.frame_index)], self.size)
		
		if not self.vulnerable:
			self.image.set_alpha(sine_wave_value())

	def actions(self,player):
		if self.status == 'attack':
			self.attack_time = pygame.time.get_ticks()
			self.direction = pygame.math.Vector2()
		elif self.status == 'move':
			self.direction = self.get_player_distance_direction(player)[1]
		else:
			self.direction = pygame.math.Vector2()

		if self.direction.x > 0:
			self.direction_facing = 'right'
		elif self.direction.x < 0:
			self.direction_facing = 'left'

	def move(self):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		self.velocity.x = self.direction.x * self.speed * self.game.dt
		# self.velocity.y = self.direction.y * speed

	def check_constraints(self, contraints:list):
		for constraint in contraints:
			if self.rect.colliderect(constraint):
				if self.direction_facing == 'right':
					self.direction_facing = 'left'
					self.rect.x + 10
				elif self.direction_facing == 'left':
					self.direction_facing = 'right'
					self.rect.x - 10

	def get_player_distance_direction(self,player):
		enemy_vec = pygame.math.Vector2(self.rect.center)
		player_vec = pygame.math.Vector2(player.rect.center)
		distance = (player_vec - enemy_vec).magnitude()
		
		if self.game.player.rect.colliderect(self.aggro_rect) and distance > 0:
			direction = (player_vec - enemy_vec).normalize()
		else:
			direction = pygame.math.Vector2()

		return (distance,direction)
	
	def get_status(self, player):
		distance = self.get_player_distance_direction(player)[0]

		if distance <= self.attack_radius and self.can_attack:
			if self.status != 'attack':
				self.frame_index = 0
			self.status = 'attack'
		elif distance <= self.aggro_range:
			self.status = 'move'
		else:
			self.status = 'move'

	def deal_damage(self):
		if self.game.player.rect.colliderect(self.rect) and self.game.player.vulnerable and not self.game.player.rolling and self.game.player.health > 0:
			self.game.player.get_damage(self.damage)

	def incoming_damage_check(self):
		for spell in self.game.player.projectiles:
			if spell.rect.colliderect(self.rect) and self.vulnerable and self.health > 0:
				self.get_damage(spell.damage)
		for weapon in self.game.player.weapon:
			if weapon.rect.colliderect(self.rect) and self.vulnerable and self.health > 0:
				self.get_damage(weapon.damage)

	def get_damage(self, damage_taken):
		if self.vulnerable:
			self.vulnerable = False
			self.hit_time = pygame.time.get_ticks()
			self.health -= damage_taken

	def hit_reaction(self):
		if not self.vulnerable and int(self.direction.x) != 0:
			self.direction *= -self.resistance
		elif not self.vulnerable and int(self.direction.x) == 0:
			if self.direction_facing == 'right':
				self.direction += (1,1)
				self.direction *= -self.resistance
			if self.direction_facing == 'left':
				self.direction -= (1,1)
				self.direction *= -self.resistance

	def cooldowns(self):
		current_time = pygame.time.get_ticks()
		if not self.can_attack:
			if current_time - self.attack_time >= self.attack_cooldown:
				self.can_attack = True

		if not self.vulnerable:
			if current_time - self.hit_time >= self.invincibility_duration:
				self.vulnerable = True

	def status_bar(self):
		health_bar = pygame.Rect((self.rect.topleft - self.game.camera.level_scroll) - (0, 20), (200 * self.health/100, 8))
		pygame.draw.rect(self.game.screen, [255,0,0], health_bar)
	
	def draw(self, surface:pygame.Surface):
		surface.blit(self.image, self.rect.topleft - self.game.camera.level_scroll)
		self.status_bar()
	 	# show aggro range
		# self.game.screen.blit(pygame.Surface((self.aggro_range, self.aggro_range)), self.aggro_rect.topleft - self.game.camera.level_scroll)

	def update(self, terrain, constraints):
		self.actions(self.game.player)
		self.incoming_damage_check()
		self.hit_reaction()
		# self.check_constraints(constraints)
		self.move()
		self.animate()
		self.get_status(self.game.player)
		self.cooldowns()

		self.rect, self.game.world.collisions = collision_adjust(self, self.velocity, self.game.dt, terrain)
		# collision handling
		if self.game.world.collisions['bottom']:
			self.velocity.y = 0

		self.aggro_rect.center = self.rect.center

		self.deal_damage()

class Player(Entity):

	def __init__(self, game, character, size, position, speed, groups):
		super().__init__(size, position, speed, groups)
		# config
		self.game = game
		self.character = character
		self.get_stats()
		self.import_character_assets()

		self.particles = []
		self.projectiles = []
		self.airborne_timer = 0
		self.spell_shards = 0
		self.weapon_sprite = pygame.sprite.GroupSingle()
		
		self.hurtbox = pygame.Rect( self.rect.topleft, (32,96))
		# movement
		# dash
		self.dash_timer = 4
		self.dash_counter = 1
		# roll
		self.roll_counter = 1
		# stat scales
		self.health_scale = CHARACTERS[self.character]["HEALTH"]
		self.magick_scale = CHARACTERS[self.character]["MAGICK"]
		self.spell_shard_scale = 2

		# spells
		self.cast_timer = self.cast_cooldown
		self.active_spell_slot = 1
		self.bound_spells = ['windblade', 'fireball']
		self.known_spells = []
		self.active_spell = self.bound_spells[self.active_spell_slot-1]
		self.current_spell_shard_count = 0

		# player status
		self.status = 'idle'
		self.attacking = False
		self.dashing = False
		self.rolling = False
		self.jumping = False
		self.in_boss_room = False
		self.heavy_fall = False
		self.vulnerable = True
		self.can_attack = True
		self.casting = False

		# animation
		self.frame_index = 0
		self.animation_speed = 0.25
		self.animation = self.animations[self.status]
		self.attack_duration = 0
		self.rect = pygame.Rect( (self.rect.x, self.rect.y), (32, 96) )

		# collision area
		self.collision_area = pygame.Rect(self.rect.x, self.rect.y, TILE_SIZE * 3, TILE_SIZE * 3)

		""" WEAPONS """
		self.weapon = []
		self.current_weapon = 'skolfen'
		self.weapon_sprite = pygame.sprite.GroupSingle()

	def get_stats(self):
		self.stats = CHARACTERS[self.character]
		self.name = self.stats['NAME']
		self.health = self.stats['HEALTH']
		self.magick = self.stats['MAGICK']
		self.speed = self.stats['SPEED']
		self.jumps = self.stats['JUMPS']
		self.jumpforce = self.stats['JUMPFORCE']
		self.roll_speed = self.stats['ROLL SPEED']
		self.roll_cooldown = self.stats['ROLL COOLDOWN']
		self.attack_cooldown = self.stats['ATK_CD']
		self.cast_cooldown = self.stats['CAST_CD']
		self.dash_distance = self.stats['DASH DIST']
		self.roll_distance = self.stats['ROLL DIST']
		self.IFRAMES = self.stats['IFRAMES']

	def import_character_assets(self):
		self.animation_keys = {'idle':[],'run':[],'jump':[],'fall':[], 'attack':[], 'roll':[]} 

		for animation in self.animation_keys:
			full_path = CHAR_PATH + animation
			
			original_images = import_folder(full_path)
			scaled_images = scale_images(original_images, self.size)
			
			self.animation_keys[animation] = import_folder(full_path)

		self.animations = self.animation_keys
	
	def animate(self):
		animation = self.animation_keys[self.status]
		self.frame_index += self.animation_speed * self.game.dt
		if self.frame_index >= len(animation):
			self.frame_index = 0
		if self.facing_right:
			self.image = pygame.transform.scale(animation[int(self.frame_index)], self.size)
		elif not self.vulnerable:
			self.image.set_alpha(sine_wave_value())
		else:
			self.image = pygame.transform.flip(pygame.transform.scale(animation[int(self.frame_index)], self.size), True, False)

	def jump(self, dt):
		if self.jumps > 0:
			self.velocity.y = -self.jumpforce
			self.jumps -= 1

	def move(self, dt):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_d] and not self.dashing and not self.rolling:
			self.facing_right = True
			self.velocity.x = self.speed
		elif keys[pygame.K_a] and not self.dashing and not self.rolling:
			self.facing_right = False
			self.velocity.x = -self.speed
		else:
			self.velocity.x = 0
		
		# jumping
		if keys[pygame.K_SPACE] and self.jumps > 0 and self.airborne_timer < 12:
			self.jump(dt)
			self.jumping = True
			self.collide_bottom = False

		# jumps reset
		if self.jumps <= 0 and self.collide_bottom:
			self.jumps = CHARACTERS[self.character]["JUMPS"]

		if self.attacking:
			self.attack_duration += 0.2 * self.game.dt
			self.velocity.x = 0

		if self.jumping:
			self.rolling = False

	def switch_active_spell(self):
		if self.active_spell_slot in [1, 2]:
			self.active_spell = self.bound_spells[self.active_spell_slot-1]

	def create_attack(self):
		self.weapon.append(
			Weapon(self.game, self, self.weapon_sprite)
		)
	
	def show_attacks(self, surface:pygame.Surface):
		for attack_rect in self.attack_rects:
			pygame.draw.rect(surface, "blue", attack_rect)

	def roll(self, dt):
		frame_scale = self.game.current_fps / 75.0
		adjusted_roll_speed = self.roll_speed * frame_scale

		if self.rolling and self.facing_right and self.collide_bottom:
			self.velocity.x += adjusted_roll_speed * dt
			# marker = pygame.Rect(self.roll_point - self.game.camera.level_scroll, (40,40))
			# pygame.draw.rect(self.game.screen, "white", marker)

		elif self.rolling and not self.facing_right and self.collide_bottom:
			self.velocity.x += -adjusted_roll_speed * dt
			# marker = pygame.Rect(self.roll_point - self.game.camera.level_scroll, (40,40))
			# pygame.draw.rect(self.game.screen, "white", marker)
	
	def dash(self, dt):
		frame_scale = self.game.current_fps / 75.0
		adjusted_dash_distance = self.dash_distance * frame_scale

		if self.dashing and self.facing_right and not self.collide_bottom:
			self.velocity.y = 0
			self.velocity.x += adjusted_dash_distance * dt
			# marker = pygame.Rect(self.dash_point - self.game.camera.level_scroll, (40,40))
			for i in range(int(self.dash_timer)):
				self.particles.append(Particle(self.game, [255, 255, 255], self.rect.center, (0, 1), 6, [pygame.sprite.Group()]))

			# pygame.draw.rect(self.game.screen, "white", marker)

		elif self.dashing and not self.facing_right and not self.collide_bottom:
			self.velocity.y = 0
			self.velocity.x += -adjusted_dash_distance * dt
			# marker = pygame.Rect(self.dash_point - self.game.camera.level_scroll, (40,40))
			for i in range(int(self.dash_timer)):
				self.particles.append(Particle(self.game, [255, 255, 255], self.rect.center, (0, 1), 6, [pygame.sprite.Group()]))
				
			# pygame.draw.rect(self.game.screen, "white", marker)

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

	def stat_bar(self):
		if int(self.roll_cooldown) < CHARACTERS[self.character]["ROLL COOLDOWN"] and self.rolling:
			self.roll_coolown_bar = pygame.Rect((self.rect.left - self.game.camera.level_scroll.x, self.rect.top - self.game.camera.level_scroll.y), ((self.hurtbox.width * self.roll_cooldown), 8))
			pygame.draw.rect(self.game.screen, [80,80,80], self.roll_coolown_bar)

	def update_projectiles(self):
		for projectile in self.projectiles:
			projectile.update()

	def incoming_damage_check(self):
		pass
		
	def get_damage(self, damage_taken):
		if self.vulnerable:
			self.vulnerable = False
			self.hit_time = pygame.time.get_ticks()
			self.health -= damage_taken

	def cooldowns(self):
		current_time = pygame.time.get_ticks()
		if not self.can_attack:
			if current_time - self.attack_time >= self.attack_cooldown:
				self.can_attack = True

		if not self.vulnerable:
			if current_time - self.hit_time >= self.IFRAMES:
				self.vulnerable = True

	def update(self, dt, surface:pygame.Surface, terrain:list):
		self.incoming_damage_check()
		self.move(dt)
		self.roll(dt)
		self.dash(dt)
		self.on_screen_check()
		self.get_status()
		self.animate()
		self.cooldowns()
		
		# update hurtbox
		self.hurtbox.center = self.rect.center - self.game.camera.level_scroll

		# adjust the player based on collisions
		self.rect, self.game.world.collisions = collision_adjust(self, self.velocity, self.game.dt, terrain)

		# collision handling
		if self.game.world.collisions['bottom']:
			self.velocity.y = 0
			self.airborne_timer = 0
			self.jumping = False
			self.jumps = CHARACTERS[self.character]["JUMPS"]
		else:
			self.airborne_timer += 1 * dt

		# heavy fall
		if int(self.velocity.y) >= 20:
			self.heavy_fall = True

		if self.game.world.collisions['bottom'] and self.heavy_fall:
			self.rolling = True
			self.velocity.y = 0
			self.heavy_fall = False			

		# dashing
		if not self.dashing and self.dash_counter <= 0 and self.collide_bottom:
			self.dash_counter = 1

		if self.dashing and self.dash_timer > 0 and not self.collide_bottom:
			self.dash_timer -= 1 * dt
			blur_surface = pygame.transform.box_blur(self.image, 4, True)
			self.image = blur_surface

		if self.dash_timer <= 0 or not self.dashing:
			self.dashing = False
			self.dash_timer = 4
		if self.collide_bottom:
			self.dashing = False

		# roll
		if not self.rolling and self.roll_counter <= 0:
			self.roll_counter = 1

		if self.rolling and self.roll_cooldown > 0 and self.collide_bottom:
			self.roll_cooldown -= 0.2 * dt

		if self.roll_cooldown <= 0:
			self.rolling = False
		
		if self.roll_cooldown < CHARACTERS[self.character]["ROLL COOLDOWN"]:
			self.roll_cooldown += 0.1 * dt  # roll cooldown
		
		# # attacking
		# if int(self.attack_duration) > 5:
		# 	self.attack_duration = 0
		# 	self.animation.frame_index = 0

		# if int(self.attack_duration) == self.animations[self.status].frame_duration:
		# 	self.attacking = False
		# 	self.attack_duration = 0

		# particles
		for particle in self.particles:
			if particle.radius <= 0:
				self.particles.remove(particle)

		# projectiles/spells
		self.update_projectiles()
		if self.cast_timer > 0 and self.casting:
			self.cast_timer -= 1 * dt

		if self.cast_timer <= 0:
			self.casting = False
			self.cast_timer = self.cast_cooldown
		# print(self.projectiles)

		# items
		if self.spell_shards > 2:
			self.spell_shards = 2

		# stats
		if self.magick > CHARACTERS[self.character]["MAGICK"]:
			self.magick = CHARACTERS[self.character]["MAGICK"]

		# draw player
		# self.show_attacks(surface)
		self.draw(surface)

class World():

	def __init__(self, game, world_data):
		# world config
		self.game = game
		self.world_data = world_data
		self.level_topleft = 0
		self.level_bottomright = 0
		
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
		self.terrain_data = import_csv_layout(world_data['terrain'])
		
		self.constraints = []
		self.constraint_data = import_csv_layout(world_data['constraint'])
		
		self.torch_positions = []
		self.torch_data = import_csv_layout(world_data['torch'])
		
		self.background_positions = []
		self.background_data = import_csv_layout(world_data['background'])
		
		self.foreground_positions = []
		self.foreground_data = import_csv_layout(world_data['foreground'])


		self.layer_data = [
			self.background_data,
			self.terrain_data,
			self.player_data,  # i need to draw the player at this point  ( i fix later )
			self.foreground_data,
			self.torch_data,
		]

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
				if int(value) == 0:
					self.enemy_spawns.append(pygame.math.Vector2(x * TILE_SIZE, y * TILE_SIZE))
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
			self.enemies.append(
				Enemy(self.game, 'rose_sentinel', 5, 96, spawn, self.game.enemy_sprites)
			)
			# break
		
	def despawn_enemy(self):
		for enemy in self.enemies:
			if enemy.health <= 0:
				enemy.kill()
				self.enemies.remove(enemy)
				self.enemy_rects.remove(enemy.rect)
				for i in range(enemy.exp):
					position = (enemy.rect.x + random.randint(-50, 50), enemy.rect.y + random.randint(-50, 50))
					self.world_items.append(Item(self.game, 'magick_shard', 'magick', ITEMS['magick']['magick_shard']["SIZE"], position, 2, self.game.item_group))
		
		# print('amount of items', len(self.world_items))

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
		for row in self.torch_data:
			x = 0
			for tile_num, tile_id in enumerate(row):
				if int(tile_id) == 18:
					self.torch_positions.append([(x * TILE_SIZE - self.game.camera.level_scroll.x, y * TILE_SIZE - self.game.camera.level_scroll.y)])
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
				self.game.playable = False
			if self.game.player.collide_bottom:
				self.game.playable = True

	def world_FX(self):
		for index, pos in enumerate(self.torch_positions):
			for x in range(3):
				self.world_particles.append(
					Particle(self.game, random.choice(seto_colors["torch1"]), ((self.torch_positions[index][0][0] + 32) + random.randint(-10, 10), self.torch_positions[index][0][1] + 42), (random.randint(-2,2), -4), 3, [pygame.sprite.Group()], torch=True)
				)
		
		for index, position in enumerate(self.torch_positions):
			torch_glow = glow_surface(TILE_SIZE*2, [20,20,40],120)
			self.game.world_brightness.blit(torch_glow, (position[0] - self.game.camera.level_scroll) - (102, 122), special_flags=pygame.BLEND_RGB_ADD)

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

	def draw_world(self, surface:pygame.Surface):
		# self.spawn_enemies()
		# draw tiles
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

class UI():
	def __init__(self, game, surface):
		self.game = game
		self.display = surface

		self.player_hud = get_image('../assets/ui/HUD/HUD.png')
		self.player_portrait = get_image('../assets/ui/HUD/alryn_faceset2.png')
		self.player_hud = scale_images([self.player_hud], (460,100))[0]
		self.player_portrait = scale_images([self.player_portrait], (87,81))[0]
		# self.spell_image = get_image()

	def update_spell_shard_count(self):
		spell_shard_img = get_image('../assets/items/magick/magick_shard/magick_shard1.png')
		self.display.blit(spell_shard_img, (40, 120))
		draw_text(self.display, f"{self.game.player.current_spell_shard_count}", [25, 150], size=32)

	def update_spell_slot(self):
		spell_slot_1_rect = pygame.Rect((1, SCREEN_HEIGHT - 121), (96,96))
		spell_1_image = get_image(SPELL_PATH+self.game.player.active_spell+'/'+self.game.player.active_spell+'1'+'.png')
		spell_1_image = scale_images([spell_1_image], (96,96))
		spell_1_image = spell_1_image[0]
		self.display.blit(spell_1_image, spell_slot_1_rect)
		# pygame.draw.rect(self.display, [0,0,0], spell_slot_1_rect)

	def update_player_HUD(self):
		# under bars
		self.health_under_bar = pygame.Rect((98, 60), (364, 26))
		self.magick_under_bar = pygame.Rect((98, 78), (364, 26))
		# bars
		self.health_bar = pygame.Rect((98, 60), (364 * self.game.player.health/self.game.player.health_scale, 26))
		self.magick_bar = pygame.Rect((90, 90), (374 * self.game.player.magick/self.game.player.magick_scale, 14))
		
		pygame.draw.rect(self.display, [0,0,0], self.health_under_bar)
		pygame.draw.rect(self.display, [0,0,0], self.magick_under_bar)
		pygame.draw.rect(self.display, [150,0,0], self.health_bar)
		pygame.draw.rect(self.display, [0,150,200], self.magick_bar)
		self.display.blit(self.player_hud, (5,10))
		self.display.blit(self.player_portrait, (25,10))
		
		if self.game.player.spell_shards > 0:
			spell_shard_1 = pygame.transform.scale(get_image('../assets/UI/HUD/HUD_SHARD.png'), (54, 30))
			self.display.blit(spell_shard_1, (105, 35))
		
		if self.game.player.spell_shards == 2:
			spell_shard_2 = pygame.transform.scale(get_image('../assets/UI/HUD/HUD_SHARD.png'), (54, 30))
			self.display.blit(spell_shard_2, (136, 35))
		
class Game():
	
	def __init__(self):
		self.setup_pygame()
		self.setup_world()

		self.particle_presets = {
			# "torch": Particle(self, random.choice(seto_colors), ((mx + random.randint(-20, 20)) + self.camera.level_scroll.x, my + random.randint(-20, 20) + self.camera.level_scroll.y), (0, -4), 3, [pygame.sprite.Group()]),
		}

		self.mouse_particles = []

	def setup_pygame(self):
		self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SCALED)
		self.scaled_display = pygame.Surface((SCREEN_SIZE[0]//3, SCREEN_SIZE[1]//3))
		self.clock = pygame.time.Clock()
		pygame.display.set_caption("A Tale Of Time")
		pygame.display.set_icon(get_image('../assets/logo.ico'))
		# pygame.display.toggle_fullscreen()

	def setup_world(self):
		self.world_brightness = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
		self.world_brightness.convert_alpha()

		# enemy sprites
		self.enemy_sprites = pygame.sprite.Group()

		# create world
		self.current_world = 1
		self.world = World(self, worlds[self.current_world])

		# create player
		self.player_sprite_group = pygame.sprite.GroupSingle()
		self.player = Player(self, "ALRYN", 96, self.world.player_spawn, CHARACTERS["ALRYN"]["SPEED"], [self.player_sprite_group])

		# create camera
		self.camera = Camera(self, 10, 250)
		
		# ui
		self.ui = UI(self, self.screen)

		# item test
		self.item_group = pygame.sprite.Group()

		self.background = get_image('../assets/background.png')
		self.midground = get_image('../assets/midground.png')
		self.foreground = get_image('../assets/foreground.png')
		self.full_background = [
			self.background,
			self.midground,
			self.foreground,
		]
		self.full_background = scale_images(self.full_background, (self.world.level_width, self.world.level_height))

	def update_background(self):
		self.screen.fill([55, 55, 92])
		self.world_brightness.fill([WORLD_BRIGHTNESS, WORLD_BRIGHTNESS, WORLD_BRIGHTNESS])
		
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
					self.player.active_spell_slot = 2
					self.player.switch_active_spell()
					pass
				elif event.button == 5:  # Mouse wheel down
					self.player.active_spell_slot = 1
					self.player.switch_active_spell()
					pass
				elif event.button == 1:
					pass

			# button released
			
			# key pressed
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_f:
					pygame.display.toggle_fullscreen()
				
				# dashing
				if event.key == pygame.K_LSHIFT and self.player.dash_counter > 0:
					pygame.key.set_repeat(0)
					self.player.dash_point = (self.player.rect.x, self.player.rect.y)
					self.player.dashing = True
					self.player.dash_counter -= 1
				
				# rolling
				if event.key == pygame.K_LSHIFT and self.player.collide_bottom and self.player.roll_counter > 0 and int(self.player.roll_cooldown) == CHARACTERS[self.player.character]["ROLL COOLDOWN"]:
					self.player.roll_point = (self.player.rect.x, self.player.rect.y)
					self.player.rolling = True
					self.player.roll_counter -= 1

				# attacking
				if event.key == pygame.K_o and self.player.collide_bottom:
					self.player.attacking = True
					self.player.create_attack()

				# spells
				if event.key == pygame.K_p: #and self.player.collide_bottom:
					if self.player.facing_right  and self.player.magick > 0 and self.player.vulnerable and self.player.cast_timer == self.player.cast_cooldown:
						self.player.casting = True
						self.player.magick -= SPELLS[self.player.active_spell][3]
						self.player.projectiles.append(
							Projectile(self, self.player.rect.center, self.player.active_spell, 'right', self.player.rect.center, 300)
						)
					if not self.player.facing_right  and self.player.magick > 0 and self.player.vulnerable and self.player.cast_timer == self.player.cast_cooldown:
						self.player.casting = True
						self.player.magick -= SPELLS[self.player.active_spell][3]
						self.player.projectiles.append(
							Projectile(self, self.player.rect.center, self.player.active_spell, 'left', self.player.rect.center, 300)
						)
				
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
			
			self.handle_events()

			# updates
			self.world.update()
			self.world.update_enemies(self.dt, self.screen, self.world.tile_rects, self.world.constraint_rects)
			self.player.update(self.dt, self.screen, self.world.tile_rects)
			self.camera.update_position()

			# drawing
			self.update_background()
			self.world.draw_world(self.screen)
			self.player.stat_bar()
			self.ui.update_player_HUD()
			self.ui.update_spell_slot()
			self.ui.update_spell_shard_count()
			self.world.update_items(self.screen)
			
			# handle projectiles
			for projectile in self.player.projectiles:
				projectile.draw(self.screen)


				if projectile.status == 'remove':
					self.player.projectiles.remove(projectile)
				else:
					if projectile.position.x >= projectile.cast_from.x + projectile.distance:
						projectile.status = 'hit'				
					if projectile.position.x <= projectile.cast_from.x - projectile.distance:
						projectile.status = 'hit'				

			# handle weapons
			if len(self.player.weapon) > 0:
				for weapon in self.player.weapon:
					weapon.draw(self.screen)

					if not self.player.attacking:
						self.player.weapon.remove(weapon)
			
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
