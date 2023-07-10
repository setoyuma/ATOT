from BLACKFORGE2 import *
from CONSTANTS import *
from projectile import *
from utils import *
from particle import Particle


	
		


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


class Item(Entity):

	def __init__(self, game, item_name, type, size, position, speed, groups):
		super().__init__(size, position, speed, groups)
		self.entity_type = 'item'
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
						self.game.player.magick_shards += 1
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


class Enemy(Entity):
	
	def __init__(self, game, enemy_name, speed, size, position, groups):
		super().__init__(size, position, speed, groups)
		self.entity_type = 'enemy'
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
		self.attacking = False
		self.aggro_rect = pygame.Rect(self.rect.topleft, (self.aggro_range, self.aggro_range))
		if self.name in ['Covenant Follower']:
			self.cast_range_rect = pygame.Rect(self.rect.topleft, (self.cast_range, self.cast_range))
			self.cast_timer = 0
		# vfx
		self.spells = []
		self.particles = []

		# animation
		self.status = 'move'
		self.frame_index = 0
		self.animation = self.animation_keys[self.status]
		self.animation_speed = 0.25

		self.hurtbox = pygame.Rect(self.rect.center, (64, 64))

		self.rects = [self.rect]

	def grab_stats(self, enemy_name):
		self.stats = ENEMIES[enemy_name]
		self.size = pygame.math.Vector2(self.stats['SPRITE SIZE'], self.stats['SPRITE SIZE'])
		self.name = self.stats['NAME']
		self.health = self.stats['HEALTH']
		self.health_scale = self.stats['HEALTH']
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

		if self.name in ['Covenant Follower']:
			self.cast_range = self.stats['CAST_RNG']

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
		elif self.direction_facing == 'left':
			self.image = pygame.transform.scale(animation[int(self.frame_index)], self.size)

		if self.name in ['Covenant Follower']:
			if self.attacking and self.status == 'attack':
				self.frame_index = len(self.animation)

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

	def attack(self):
		if self.name in ['Covenant Follower']:
			if self.game.player.rect.colliderect(self.cast_range_rect) and self.facing_right:
				self.spells.append(
					Projectile(
						self.game,
						(self.rect.right + 5, self.rect.top), 
						'wrath_of_alwyd', 
						'right', 
						(self.rect.right + 5, self.rect.top), 
						300
					)
				)
			if self.game.player.rect.colliderect(self.cast_range_rect) and not self.facing_right:
				self.spells.append(
					Projectile(
						self.game,
						(self.rect.left - 5, self.rect.top), 
						'wrath_of_alwyd', 
						'left', 
						(self.rect.left - 5, self.rect.top), 
						300
					)
				)

	def move(self):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		self.velocity.x = self.direction.x * self.speed * self.game.dt
		if not self.gravity:
			self.velocity.y = self.direction.y * self.speed * self.game.dt

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
			if self.name in ['Rose Sentinel', 'Sepparition', 'Covenant Follower']:
				self.game.player.get_damage(self.damage)
		
	def incoming_damage_check(self):
		for spell in self.game.player.projectiles:
			if spell.rect.colliderect(self.rect) and self.vulnerable and self.health > 0:
				self.get_damage(spell.damage)
		for weapon in self.game.player.weapon:
			if weapon.rect.colliderect(self.rect) and self.vulnerable and self.health > 0:
				self.get_damage(weapon.damage)

	def get_damage(self, damage_taken, type=None):
		if self.vulnerable:
			self.vulnerable = False
			self.hit_time = pygame.time.get_ticks()
			self.health -= damage_taken

		if type == 'melee':
			self.game.camera.shake = True
			self.game.camera.shake_timer = damage_taken

	def hit_reaction(self):
		if not self.vulnerable and int(self.direction.x) != 0:
			self.direction *= -self.resistance
			pass
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
			self.attacking = True
			self.animation_speed = 0.15
			self.status = 'attack'
			if current_time - self.attack_time >= self.attack_cooldown:
				self.can_attack = True
				self.attacking = False

		if not self.vulnerable:
			if current_time - self.hit_time >= self.invincibility_duration:
				self.vulnerable = True

	def status_bar(self):
		health_bar = pygame.Rect((self.rect.topleft - self.game.camera.level_scroll) - (0, 20), (200 * self.health/self.health_scale, 8))
		pygame.draw.rect(self.game.screen, [255,0,0], health_bar)
	
	def draw(self, surface:pygame.Surface):
		surface.blit(self.image, self.hurtbox.topleft - self.game.camera.level_scroll)
		self.status_bar()
		
		# show cast range
		# if self.name in ['Covenant Follower']:
		# 	self.game.screen.blit(pygame.Surface((self.cast_range, self.cast_range)), self.cast_range_rect.topleft - self.game.camera.level_scroll)

	 	# show aggro range
		# self.game.screen.blit(pygame.Surface((self.aggro_range, self.aggro_range)), self.aggro_rect.topleft - self.game.camera.level_scroll)

	def update_spells(self, player):
		for spell in self.spells:
			spell.update()
			if spell.rect.colliderect(player.rect) and self.game.player.vulnerable and not self.game.player.rolling and self.game.player.health > 0:
				spell.collided = True
				spell.status = 'hit'
				player.get_damage(spell.damage)
	
	def show_rects(self, surface:pygame.Surface):
		for rect in self.rects:
			surf = pygame.Surface((rect.width, rect.height))
			surf.fill('red')
			surface.blit(surf, rect.topleft - self.game.camera.level_scroll)

	def update(self, terrain, constraints):
		self.actions(self.game.player)
		self.incoming_damage_check()
		self.hit_reaction()
		# self.check_constraints(constraints)
		self.move()
		self.cooldowns()
		self.animate()
		self.get_status(self.game.player)

		if self.direction.x > 0:
			self.facing_right = True
		if self.direction.x < 0:
			self.facing_right = False

		self.rect, self.game.world.collisions = collision_adjust(self, self.velocity, self.game.dt, terrain)
		
		self.hurtbox.topleft = self.rect.topleft
		
		# collision handling
		if self.game.world.collisions['bottom']:
			self.velocity.y = 0

		self.aggro_rect.center = self.rect.center
		if self.name in ['Covenant Follower']:
			self.cast_range_rect.center = self.rect.center
		self.deal_damage()

		self.update_spells(self.game.player)

		if self.name in ['Covenant Follower'] and self.attacking:
				self.cast_timer += 1
		else:
			self.cast_timer = 0

		if round(int(self.cast_timer)) == len(self.animation):
			self.attack()


class Player(Entity):

	def __init__(self, game, character, size, position, speed, groups):
		super().__init__(size, position, speed, groups)
		# config
		self.savename = ''
		self.savedata = ''
		self.saveslot = ''
		self.entity_type = 'player'
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
		self.magick_shards = 0

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
		self.animator = NewAnimator(self.game, self, self.animation_speed)


		# self.animation = self.animations[self.status]

		self.rect = pygame.Rect( (self.rect.x, self.rect.y), (32, self.image.get_height()/2) )

		# collision area
		self.collision_area = pygame.Rect(self.rect.x, self.rect.y, TILE_SIZE * 3, TILE_SIZE * 3)

		""" WEAPONS """
		self.weapon = []
		self.current_weapon = 'skolfen'
		self.weapon_sprite = pygame.sprite.GroupSingle()

		# attacking
		self.attack_time = 0
		self.combo = 0


		self.rects = [self.rect]

	def get_stats(self):
		self.stats = CHARACTERS[self.character]
		self.hitboxes = self.stats['hitboxes']
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
		self.animation_keys = {'idle':[],'run':[],'jump':[],'fall':[], 'attack/overhead/1':[], 'attack/overhead/2':[], 'roll':[]} 

		for animation in self.animation_keys:
			full_path = CHAR_PATH + animation
			
			original_images = new_import_folder(full_path)
			scaled_images = scale_images(original_images, self.size)
			
			self.animation_keys[animation] = new_import_folder(full_path)

		self.animations = self.animation_keys
	
	def animation_handler(self):
		animation = self.animator.animation
		self.animator.run(self.animations[self.status])

		if self.status == f'attack/overhead/{self.combo}':
			if int(self.animator.frame_index) == len(animation) - 1:
				self.animator.frame_index = self.animator.frame_index - 1
				print('attack over')
		
		if not self.vulnerable:
			self.image.set_alpha(sine_wave_value())

		# self.image = alryn_pallete_swap(
		# 	self.image,
		# 	[255, 255, 0],
		# 	[140, 255, 0]
		# )

	def jump(self, dt):
		if self.jumps > 0:
			self.velocity.y = -self.jumpforce
			self.jumps -= 1

	def move(self, dt):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_d] and not self.dashing and not self.rolling and '/' not in self.status:
			self.facing_right = True
			self.velocity.x = self.speed
		elif keys[pygame.K_a] and not self.dashing and not self.rolling and '/' not in self.status:
			self.facing_right = False
			self.velocity.x = -self.speed
		else:
			self.velocity.x = 0
		
		# jumping
		if keys[pygame.K_SPACE] and self.jumps > 0 and self.airborne_timer < 12 and '/' not in self.status:
			self.jump(dt)
			self.jumping = True
			self.collide_bottom = False

		# jumps reset
		if self.jumps <= 0 and self.collide_bottom:
			self.jumps = CHARACTERS[self.character]["JUMPS"]

		if self.jumping:
			self.rolling = False

	def switch_active_spell(self):
		if self.active_spell_slot in [1, 2]:
			self.active_spell = self.bound_spells[self.active_spell_slot-1]

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
		elif self.velocity.y > 1.5:
			self.status = 'fall'
		else:
			if self.velocity.x != 0:
				self.status = 'run'
			elif self.velocity.x < 1:
				self.status = 'idle'
		if self.attacking:
			self.status = f'attack/overhead/{self.combo}'
		if self.rolling:
			self.status = 'roll'
	
	def check_combo(self):
		# reset combo if it reaches max
		if self.combo >= 2:
			self.combo = 1

	def draw(self, surface:pygame.Surface):
		image_offset = ( -60, -80)
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

	def update_projectiles(self, collideables:list):
		for projectile in self.projectiles:
			projectile.update()
			for object_list in collideables:
				for obj in object_list:
					if projectile.rect.colliderect(obj):
						projectile.collided = True
						projectile.status = 'hit'

	def incoming_damage_check(self):
		pass
		
	def get_damage(self, damage_taken):
		if self.vulnerable:
			self.vulnerable = False
			self.hit_time = pygame.time.get_ticks()
			self.health -= damage_taken

	def attack(self):
		self.animator.frame_index = 0
		self.combo += 1
		self.attack_time = pygame.time.get_ticks()
		self.attacking = True
		self.can_attack = False
	
	def create_attack(self):
		if self.facing_right:
			hitbox = self.hitboxes['overhead'+str(self.combo)]
			if int(self.animator.frame_index) == hitbox[0]:
				# print('attack active on frame', int(self.animator.frame_index))
				offset = pygame.math.Vector2(hitbox[1][0], hitbox[1][1])
				final_hitbox = pygame.Rect(self.rect.bottomright - offset, (hitbox[1][2], hitbox[1][3]))
				self.rects.append(final_hitbox)

				# collision checks
				for enemy in self.game.world.enemies:
					if final_hitbox.colliderect(enemy.rect):
						enemy.get_damage(5, type='melee')

		if not self.facing_right:
			hitbox = self.hitboxes['overhead'+str(self.combo)]
			if int(self.animator.frame_index) == hitbox[0]:
				# print('attack active on frame', int(self.animator.frame_index))
				offset = pygame.math.Vector2(-hitbox[1][0], hitbox[1][1])
				final_hitbox = pygame.Rect(self.rect.bottomright - offset, (hitbox[1][2], hitbox[1][3]))
				self.rects.append(final_hitbox)
		
				# collision checks
				for enemy in self.game.world.enemies:
					if final_hitbox.colliderect(enemy.rect):
						enemy.get_damage(5, type='melee')

	def cooldowns(self):
		current_time = pygame.time.get_ticks()
		if self.attacking:
			if current_time - self.attack_time >= self.attack_cooldown:
				self.can_attack = True
				self.attacking = False
				self.combo = 0
				self.frame_index = 0
				self.rects = [self.rect]
		if not self.vulnerable:
			if current_time - self.hit_time >= self.IFRAMES:
				self.vulnerable = True

	def show_rects(self, surface:pygame.Surface):
		for rect in self.rects:
			surf = pygame.Surface((rect.width, rect.height))
			surf.fill('white')
			surface.blit(surf, rect.topleft - self.game.camera.level_scroll)

	def update(self, dt, surface:pygame.Surface, terrain:list):
		self.incoming_damage_check()
		self.move(dt)
		self.roll(dt)
		self.dash(dt)
		self.on_screen_check()
		self.get_status()
		self.animation_handler()
		self.cooldowns()
		self.check_combo()
		
		if self.attacking:
			self.create_attack()

		
		# update hurtbox
		self.hurtbox.center = self.rect.center - self.game.camera.level_scroll

		# adjust the player based on collisions
		self.rect, self.game.world.collisions = collision_adjust(self, self.velocity, self.game.dt, terrain)

		# collision handling
		if self.game.world.collisions['bottom']:
			self.collide_bottom = True
			self.velocity.y = 0
			self.airborne_timer = 0
			self.jumping = False
			self.jumps = CHARACTERS[self.character]["JUMPS"]
		else:
			self.airborne_timer += 1 * dt

		# heavy fall
		if int(self.velocity.y) >= 30:
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
		
		# particles
		for particle in self.particles:
			if particle.radius <= 0.1:
				self.particles.remove(particle)

		# projectiles/spells
		self.update_projectiles([self.game.world.enemy_rects])
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

		# if self.attacking:
		# 	print(int(self.animator.frame_index)  + 1)

		# print('my saveslot',self.saveslot, 'my savename', self.savename)

		

