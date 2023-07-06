import random, time
from math import sin
from BLACKFORGE2 import *
from CONSTANTS import *

from world_data import worlds,world_names, music
from entities import *
from scenes import *

""" GAME """
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

		self.particles = []

		self.show_fps = False

	def setup_pygame(self):
		self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SCALED)
		self.scaled_display = pygame.Surface((SCREEN_SIZE[0]//3, SCREEN_SIZE[1]//3))
		self.clock = pygame.time.Clock()
		pygame.display.set_caption("A Tale Of Time")
		pygame.display.set_icon(get_image('../assets/logo.ico'))
		# pygame.display.toggle_fullscreen()
		pygame.mixer.init()

	def setup_world(self):
		self.world_brightness = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
		self.world_brightness.convert_alpha()

		# enemy sprites
		self.enemy_sprites = pygame.sprite.Group()

		# create world
		self.current_world = 3
		self.world = World(self, worlds[self.current_world])

		# create player
		self.player_sprite_group = pygame.sprite.GroupSingle()
		self.player = Player(self, "ALRYN", 96, self.world.player_spawn, CHARACTERS["ALRYN"]["SPEED"], [self.player_sprite_group])

		# create camera
		self.camera = Camera(self, 10, 225)
		
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

		print(f'../assets/music/{world_names[self.current_world]}/{music[world_names[self.current_world]]}')
		pygame.mixer.music.load(f'../assets/music/{world_names[self.current_world]}/{music[world_names[self.current_world]]}.wav')
		pygame.mixer.music.play(-1)
		pygame.mixer.music.set_volume(0.1)

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
					for i in range(10):
						self.particles.append(
							Particle(
								self,
								[255,255,255],
								(self.mx, self.my) + self.camera.level_scroll,
								(random.randint(-10,10), random.randint(-10,10)),
								20,
								[],
								gravity=True,
								physics=True
							)
						)
					pass

			# button released
			
			# key pressed
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_F8:
					self.show_fps = not self.show_fps

				if event.key == pygame.K_f:
					pygame.display.toggle_fullscreen()
				
				# dashing
				if event.key == pygame.K_LSHIFT and self.player.dash_counter > 0 and not self.player.collide_bottom:
					play_sound('../assets/sounds/dashing.wav')
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
					pass
					# self.player.attacking = True
					# self.player.create_attack()

				# spells
				if event.key == pygame.K_p: #and self.player.collide_bottom:
					if self.player.facing_right  and self.player.magick > 0 and self.player.vulnerable and self.player.cast_timer == self.player.cast_cooldown:
						self.player.casting = True
						self.player.magick -= SPELLS[self.player.active_spell][3]
						self.player.projectiles.append(
							Projectile(self, self.player.rect.center, self.player.active_spell, 'right', self.player.rect.center, 300)
						)
						play_sound(f'../assets/sounds/{self.player.active_spell}.wav')
					if not self.player.facing_right  and self.player.magick > 0 and self.player.vulnerable and self.player.cast_timer == self.player.cast_cooldown:
						self.player.casting = True
						self.player.magick -= SPELLS[self.player.active_spell][3]
						self.player.projectiles.append(
							Projectile(self, self.player.rect.center, self.player.active_spell, 'left', self.player.rect.center, 300)
						)
						play_sound(f'../assets/sounds/{self.player.active_spell}.wav')

				
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
			
			self.mx, self.my = pygame.mouse.get_pos()
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
			self.world.update_FX(self.screen)
			
			
			for p in self.particles:
				p.emit()

				if p.radius <= 0.1:
					self.particles.remove(p)

			# handle player projectiles
			for projectile in self.player.projectiles:
				projectile.draw(self.screen)


				if projectile.status == 'remove':
					self.player.projectiles.remove(projectile)
				else:
					if projectile.position.x >= projectile.cast_from.x + projectile.distance:
						projectile.status = 'hit'				
					if projectile.position.x <= projectile.cast_from.x - projectile.distance:
						projectile.status = 'hit'				

			# handle enemy projectiles
			for enemy in self.world.enemies:
				if enemy.name in ['Covenant Follower']:
					for projectile in enemy.spells:
						projectile.draw(self.screen)

						if projectile.status == 'remove':
							enemy.spells.remove(projectile)
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
			
			if self.show_fps:
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
