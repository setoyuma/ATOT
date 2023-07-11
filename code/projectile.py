from BLACKFORGE2DEV import *
from CONSTANTS import *

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
		self.image = self.animation[0]
		self.animation_speed = 0.25
		self.rect = pygame.Rect(self.position, self.size)

	def import_assets(self):
		self.animation_keys = {'fireball':[],'windblade':[], 'wrath_of_alwyd':[], 'wind_sparks':[], 'fire_sparks':[], 'alwyd_sparks':[]} 

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
					self.status = 'hit'
					
	def create_hitspark_animation(self):
		hitspark_images = []  # Placeholder list for demonstration
		hitspark_pos = self.rect.center
		# Create hitspark animation using hitspark_images and hitspark_pos
		# ...
	
	def draw(self, surface:pygame.Surface):
		surface.blit(self.image, self.rect.topleft - self.game.world.camera.level_scroll)

	def handle_status(self):
		if self.status == 'hit' or self.collided:
			match self.projectile_type:
				case 'windblade':
					self.projectile_type = 'wind_sparks'
				case 'fireball':
					self.projectile_type = 'fire_sparks'
				case 'wrath_of_alwyd':
					self.projectile_type = 'alwyd_sparks'
		
			if self.frame_index + 1 >= len(self.animations[self.projectile_type]):
				self.status = 'remove'

	def update(self):
		self.animate()
		match self.direction:
			case 'right':
				if self.status not in ['hit', 'remove'] and not self.collided:
					self.position.x += self.speed * self.game.dt
			case 'left':
				if self.status not in ['hit', 'remove'] and not self.collided:
					self.position.x += -self.speed * self.game.dt

		self.rect.center = self.position
		self.check_collision([self.game.world.tile_rects])
		self.handle_status()

