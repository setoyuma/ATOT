import pygame as pg

class Projectile(pg.sprite.Sprite):
	def __init__(self, player):
		# Call the parent class (Sprite) constructor
		super().__init__()
		self.player = player
		self.image = pg.Surface([4, 10])
		self.image.fill("black")

		self.rect = pg.Rect(self.player.rect.right, self.player.rect.centery, 20, 20)

	def update(self, ):
		pg.display.get_surface().blit(self.image, (self.rect.x, self.rect.y))
		if self.player.facing_right:
			self.rect.x += 3
		else:
			self.rect.x -= 3
