from BLACKFORGE2 import *
from CONSTANTS import *


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
