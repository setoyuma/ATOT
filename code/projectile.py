from saviorsystems.REDFORGE import *

class Projectile(pygame.sprite.Sprite):
	def __init__(self, pos:tuple, size:int, speed:int, damage:int, terrain_sprites:pygame.sprite.Group, groups:pygame.sprite.Group, offset:pygame.math.Vector2):
		super().__init__(groups)
		self.pos = pos
		# print(self.pos)
		self.size = pygame.math.Vector2(size,size)
		self.image = pygame.Surface((self.size.x,self.size.y))
		self.image.fill((255,255,255))
		self.rect = pygame.Rect(pos[0], pos[1], self.size.x, self.size.y)
		self.speed = speed
		self.damage = damage
		self.terrain = terrain_sprites
		mx, my = pygame.mouse.get_pos()
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

		angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))

	def check_collisions(self):
		for sprite in self.terrain.sprites():
			if self.rect.colliderect(sprite.rect):
				self.kill()

	def update(self, offset):
		self.check_collisions()
		self.pos = (self.pos[0]+self.dir[0]*self.speed + offset.x, 
					self.pos[1]+self.dir[1]*self.speed + offset.y)
		self.rect.center = self.pos