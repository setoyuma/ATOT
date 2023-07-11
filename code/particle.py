from BLACKFORGE2DEV import *
from CONSTANTS import *
from utils import *


class Particle(pygame.sprite.Sprite):
	def __init__(self, game, color:list, position:tuple, velocity:tuple, radius:int, groups, glow=False, gravity=False, torch=False, physics=False, image_path='', circle=False):
		# super().__init__(groups)
		self.entity_type = "particle"
		self.game = game
		self.glow = glow
		self.circle = circle
		self.torch = torch
		self.gravity = gravity
		self.physics = physics
		self.color = color
		self.position = pygame.math.Vector2(position)
		self.velocity = pygame.math.Vector2(velocity)
		self.radius = radius
		self.has_image = False
		self.image_path = image_path
		if len(self.image_path) > 0:
			self.has_image = True
			self.image = scale_images([get_image(self.image_path)], (self.radius, self.radius))[0]
		else:
			self.image = pygame.Surface((self.radius, self.radius))
			self.image.set_colorkey([0,0,0])
		self.rect = pygame.Rect(self.position, (self.radius, self.radius))

	def collision_test(self):
		self.rect, self.game.world.collisions = collision_adjust(self, self.velocity, self.game.dt, self.game.world.tile_rects)

		if self.game.world.collisions['bottom']:
			self.velocity.y = 0

	def emit(self):
		if self.glow:
			glow = glow_surface(int(self.radius*2), [20,20,20], 100)
			self.game.screen.blit(glow, (self.rect.x - 8, self.rect.y - 12) - self.game.world.camera.level_scroll, special_flags=BLEND_RGB_ADD)
		if self.gravity:
			self.velocity.y += 0.08 * self.game.dt 
		if self.physics:
			self.collision_test()
		else:
			if self.torch:
				self.velocity.x = 0.1
				# self.velocity.y = -float(random.randint(1, 10)) * self.game.dt
				self.position.x += self.velocity.x * self.game.dt
			else:
				self.position.x += self.velocity.x * self.game.dt

			self.position.y += self.velocity.y * self.game.dt
			self.rect.topleft = self.position
		self.radius -= 0.1 * self.game.dt

		if self.has_image:
			if self.radius > 0:
				self.game.screen.blit(self.image, [int(self.rect.x), int(self.rect.y)] - self.game.world.camera.level_scroll)
		else:
			if self.circle:
				if self.radius > 0:
					pygame.draw.circle(self.game.screen, self.color, [int(self.rect.x), int(self.rect.y)] - self.game.world.camera.level_scroll, int(self.radius))
			else:
				if self.radius > 0:
					surf = pygame.Surface((int(self.radius), int(self.radius)))
					surf.fill(random.choice(seto_colors["torch1"]))
					self.game.screen.blit(surf, self.rect.topleft - self.game.world.camera.level_scroll)
				# pygame.draw.rect(self.game.screen, self.color, self.rect)
