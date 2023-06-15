import pygame


""" Game Class With Zoom Feature ( has bad pixalation/scaling issues ) """
"""
class Game():
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode(SCREEN_SIZE)
		self.scaled_display = pygame.Surface((SCREEN_SIZE[0]//3, SCREEN_SIZE[1]//3))
		pygame.display.set_caption("Example")
		self.clock = pygame.time.Clock()
		self.player_sprite_group = pygame.sprite.GroupSingle()

		self.current_level = 2
		self.level = Level(self, levels[self.current_level], self.screen)

		# camera
		self.camera = Camera(self, 20)
		self.zoom_factor = 1.0  # Initial zoom factor

		self.background_objects = [
			[
				0.25,
				[100, 250, 80, 300]
			],
			[
				0.25,
				[380, 120, 80, 100]
			],
			[
				0.5,
				[550, 200, 80, 280]
			],
		]

	def draw_fps(self):
		fpsCounter = int(self.clock.get_fps())
		draw_text(self.screen, f"FPS: {fpsCounter}", [900, 20])

	def handle_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 4:  # Mouse wheel up
					self.zoom_factor += 0.1
				if event.button == 5:  # Mouse wheel down
					self.zoom_factor -= 0.1
					if self.zoom_factor < 0.1:
						self.zoom_factor = 0.1
				if event.button == 1:
					self.player.attacking = True
			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					self.player.attacking = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_f:
					pygame.display.toggle_fullscreen()
				if event.key == pygame.K_LSHIFT and self.player.dash_counter > 0:
					self.player.dashing = True
					self.player.dash_counter -= 1
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LSHIFT:
					self.player.dashing = False

	def run(self):
		running = True
		while running:
			self.screen.fill([180, 20, 80])
			self.scaled_display.fill([180, 20, 80])

			for object in self.background_objects:
				object_rect = pygame.Rect(
					object[1][0] - self.camera.level_scroll.x * object[0] * self.zoom_factor, 
					object[1][1] - self.camera.level_scroll.y * object[0] * self.zoom_factor,
					object[1][2] * self.zoom_factor,
					object[1][3] * self.zoom_factor
				)
				if object[0] == 0.25:
					pygame.draw.rect(self.screen, [14, 222, 150], object_rect)
				elif object[0] == 0.5:
					pygame.draw.rect(self.screen, [9, 91, 85], object_rect)

			self.handle_events()

			for projectile in self.player.projectiles:
				projectile.update(self.camera.level_scroll)

			print(self.player.dash_counter)

			self.camera.update_position()
			self.level.draw_level(self.screen)
			self.level.update_level()
			self.player.update(self.screen, self.level.terrain)
			self.draw_fps()
			self.clock.tick(FPS)

			# Scale the game screen to apply the zoom factor
			scaled_screen = pygame.transform.scale(self.screen, (int(SCREEN_SIZE[0] * self.zoom_factor), int(SCREEN_SIZE[1] * self.zoom_factor)))
			self.scaled_display.blit(scaled_screen, (0, 0))
			self.screen.blit(pygame.transform.scale(self.scaled_display, SCREEN_SIZE), (0, 0))

			pygame.display.flip()
"""
game = Game()
game.run()
