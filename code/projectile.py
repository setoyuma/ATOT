from saviorsystems.REDFORGE import *

class Projectile(pygame.sprite.Sprite):
	def __init__(self, type:str, pos:tuple, size:int, speed:int, damage:int, terrain_sprites:pygame.sprite.Group, groups:pygame.sprite.Group, offset:pygame.math.Vector2):
		super().__init__(groups)
		self.pos = pos
		self.type = type
		# print(self.pos)
		self.size = pygame.math.Vector2(size,size)
		self.rect = pygame.Rect(pos[0], pos[1], self.size.x, self.size.y)
		self.speed = speed
		self.damage = damage
		self.terrain = terrain_sprites
		mx, my = pygame.mouse.get_pos()
		self.import_assets()
		# print(mx, my)
		# print(pos)
		self.dir = (mx - pos[0], my - pos[1])
		length = math.hypot(*self.dir)
		if length == 0.0:
			self.dir = (0, -1)
		else:
			self.dir = (self.dir[0]/length, self.dir[1]/length)
		# print(self.dir)
		# print("\n")

		self.angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))

		self.frame_index = 0
		self.animation_speed = 0.80
		self.image = self.animations[self.type][self.frame_index]

	def import_assets(self):
		character_path = '../assets/spells/'
		self.animations = {f'{self.type}':[],}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = scale_images(import_folder(full_path), self.size)

	def animate(self):
		animation = self.animations[self.type]

		# loop over frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		image = animation[int(self.frame_index)]
		self.image = image
		self.image = pygame.transform.rotate(self.image, self.angle)

	def check_collisions(self):
		for sprite in self.terrain.sprites():
			if self.rect.colliderect(sprite.rect):
				self.kill()

	def update(self, offset):
		self.check_collisions()
		self.pos = (self.pos[0]+self.dir[0]*self.speed + offset.x, 
					self.pos[1]+self.dir[1]*self.speed + offset.y)
		self.rect.center = self.pos
		self.animate()