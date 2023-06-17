from BLACKFORGE2 import *

class Projectile(pygame.sprite.Sprite):
	def __init__(self, game, type:str, pos:tuple, size:int, speed:int, damage:int, terrain_sprites:pygame.sprite.Group, groups:pygame.sprite.Group, offset:pygame.math.Vector2):
		super().__init__(groups)
		self.game = game
		self.pos = pos
		self.type = type
		self.size = pygame.math.Vector2(size,size)
		self.rect = pygame.Rect(pos[0], pos[1], self.size.x, self.size.y)
		self.speed = speed
		self.damage = damage
		self.targeted = False
		self.terrain = terrain_sprites
		self.import_assets()

		mx, my = pygame.mouse.get_pos()
		self.dir = (mx - pos[0], my - pos[1])
		length = math.hypot(*self.dir)
		if length == 0.0:
			self.dir = (0, -1)
		else:
			self.dir = (self.dir[0]/length, self.dir[1]/length)

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
		if self.targeted:
			self.image = image
			self.image = pygame.transform.rotate(self.image, self.angle)
		else:
			self.image = image

	def check_collisions(self):
		for sprite in self.terrain.sprites():
			if self.rect.colliderect(sprite.rect):
				self.kill()

	def update(self, offset):
		# self.check_collisions()
		self.pos = (
			self.pos[0]+self.dir[0]*self.speed + offset.x * self.game.dt,
			self.pos[1]+self.dir[1]*self.speed + offset.y * self.game.dt
			)
		self.rect.x += self.pos[0]
		self.rect.y += self.pos[1]
		print(self.pos)
		self.animate()