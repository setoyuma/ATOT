from BLACKFORGE2 import *
from CONSTANTS import *
from entities import *
from particle import *
from utils import *
from world_data import *
from world import World

class Scene:
	def __init__(self, game,):
		self.game = game
		self.active = True
		self.obscured = False

	def update(self):
		pass

	def draw(self):
		pass

	def check_universal_events(self, pressed_keys, event):
		quit_attempt = False
		if event.type == pygame.QUIT:
			quit_attempt = True
		elif event.type == pygame.KEYDOWN:
			alt_pressed = pressed_keys[pygame.K_LALT] or \
				pressed_keys[pygame.K_RALT]
			if event.key == pygame.K_F4 and alt_pressed:
				quit_attempt = True
		if quit_attempt:
			pygame.quit()
			sys.exit()


class Launcher(Scene):
	
	def __init__(self, game):
		super().__init__(game)
		self.scene_type = 'launcher'
		self.logo = scale_images([get_image("../assets/ui/menu/main_menu/book50.png")], (1000, 1000))[0]
		self.game.screen = pygame.display.set_mode((1000,600))
		new_img = '../assets/ui/buttons/New.png'
		play_img = '../assets/ui/buttons/Play.png'
		self.buttons = [
			Button(game, "", (725, 350), None, new_img, new_img),
			Button(game, "", (725, 455), self.load_world, play_img, play_img),
		]

	def import_character_assets(self):
		self.animation_keys = {'idle':[],'loading':[]} 

		for animation in self.animation_keys:
			full_path = CHAR_PATH + animation
			
			original_images = import_folder(full_path)
			scaled_images = scale_images(original_images, self.size)
			
			self.animation_keys[animation] = import_folder(full_path)

		self.animations = self.animation_keys
	
	def animate(self):
		animation = self.animation_keys[self.status]
		self.frame_index += self.animation_speed * self.game.dt
		if self.frame_index >= len(animation):
			self.frame_index = 0
		if self.facing_right:
			self.image = pygame.transform.scale(animation[int(self.frame_index)], self.size)
		elif not self.vulnerable:
			self.image.set_alpha(sine_wave_value())
		else:
			self.image = pygame.transform.flip(pygame.transform.scale(animation[int(self.frame_index)], self.size), True, False)

	def patch_notes(self):
		patch_notes_rect = pygame.Rect((100,150),(200,175))
		draw_text(self.game.screen, "Patch Notes", (280,100), color="black")
		draw_text(self.game.screen,  f"{notes['Launcher']}", (280,150), color="black")
		draw_text(self.game.screen,  f"{notes['Game']}", (280,170), color="black")

	def load_world(self):
		self.game.scenes = [WorldScene(self.game)]

	def update(self):
		for event in pygame.event.get():
			for button in self.buttons:
				button.update(event)

			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

	def draw(self):
		self.game.screen.blit(self.logo, (0,-200))
		# self.game.screen.fill([0,0,0])
		
		self.patch_notes()


		for button in self.buttons:
			button.draw()





class WorldScene(Scene):
	def __init__(self, game):
		super().__init__(game)
		self.scene_type = 'world'
		self.game.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SCALED)
		self.game.current_level = 3
		self.game.world = World(game, worlds[self.game.current_level])
		self.events = True
		self.player = self.game.player
		self.world = self.game.world
		# pygame.display.toggle_fullscreen()

	def update(self):
		if not self.events:
			return

		for event in pygame.event.get():
			self.game.mx, self.game.my = pygame.mouse.get_pos()
			# quit
			if event.type == pygame.QUIT:
				print('Game Closed\n')
				pygame.quit()
				sys.exit()

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
						self.game.particles.append(
							Particle(
								self.game,
								[255,255,255],
								(self.game.mx, self.game.my) + self.game.camera.level_scroll,
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
				if event.key == pygame.K_ESCAPE:
					if len(self.game.scenes) == 1:
						self.game.scenes.append(RadialMenu(self.game))
						self.events = False
				if event.key == pygame.K_F8:
					self.game.show_fps = not self.game.show_fps

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
					# add this once we have damage animations (and self.player.vulnerable)
					if self.player.facing_right  and self.player.magick > 0 and self.player.cast_timer == self.player.cast_cooldown:
						self.player.casting = True
						self.player.magick -= SPELLS[self.player.active_spell][3]
						self.player.projectiles.append(
							Projectile(self.game, self.player.rect.center, self.player.active_spell, 'right', self.player.rect.center, 300)
						)
						play_sound(f'../assets/sounds/{self.player.active_spell}.wav')
					if not self.player.facing_right  and self.player.magick > 0 and self.player.vulnerable and self.player.cast_timer == self.player.cast_cooldown:
						self.player.casting = True
						self.player.magick -= SPELLS[self.player.active_spell][3]
						self.player.projectiles.append(
							Projectile(self.game, self.player.rect.center, self.player.active_spell, 'left', self.player.rect.center, 300)
						)
						play_sound(f'../assets/sounds/{self.player.active_spell}.wav')

				
				# player hud testing
				if event.key == pygame.K_h:
					self.player.health -= 10
				if event.key == pygame.K_m:
					self.player.magick -= 5
				if event.key == pygame.K_s:
					self.player.spell_shards += 1

	def draw(self):
		# updates
		self.game.world.update()
		self.game.world.update_enemies(self.game.dt, self.game.screen, self.game.world.tile_rects, self.game.world.constraint_rects)
		self.player.update(self.game.dt, self.game.screen, self.game.world.tile_rects)
		self.game.camera.update_position()

		# drawing
		self.game.update_background()
		self.game.world.draw_world(self.game.screen)
		self.player.stat_bar()
		self.game.ui.update_player_HUD()
		self.game.ui.update_spell_slot()
		self.game.ui.update_spell_shard_count()
		self.game.world.update_items(self.game.screen)
		self.game.world.update_FX(self.game.screen)

		for p in self.game.particles:
			p.emit()

			if p.radius <= 0.1:
				self.game.particles.remove(p)

		# handle player projectiles
		for projectile in self.player.projectiles:
			projectile.draw(self.game.screen)


			if projectile.status == 'remove':
				self.player.projectiles.remove(projectile)
			else:
				if projectile.position.x >= projectile.cast_from.x + projectile.distance:
					projectile.status = 'hit'				
				if projectile.position.x <= projectile.cast_from.x - projectile.distance:
					projectile.status = 'hit'				

		# handle enemy projectiles
		for enemy in self.game.world.enemies:
			if enemy.name in ['Covenant Follower']:
				for projectile in enemy.spells:
					projectile.draw(self.game.screen)

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
				weapon.draw(self.game.screen)

				if not self.player.attacking:
					self.player.weapon.remove(weapon)
		
		if self.game.show_fps:
			self.game.draw_fps()
		# for proj in self.player.projectiles:
		# 	proj.draw(self.game.screen)

		self.game.draw_fps()


class RadialMenu(Scene):
	def __init__(self, game):
		super().__init__(game)
		self.scene_type = 'radial menu'
		self.menu_center = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
		self.icons = import_folder("../assets/ui/menu/")
		self.rotation = 0 # keep track of how much the menu has rotated
		self.target_angle = 0
		self.section_radius = 200  # distance from the center to each section
		self.sections = len(self.icons) # resume // settings // inventory // spells // equipment
		self.section_arc = 360 / self.sections
		self.button = Button(game, "", (SCREEN_WIDTH//2+16, SCREEN_HEIGHT//2-184), self.callback, base=(0,0,100,50), hovered=(0,0,100,50))
		self.options = ["Equipment", "Grimoire", "Inventory", "Settings"]
		self.selected = 0

	def update(self):
		pressed_keys = pygame.key.get_pressed()
		for event in pygame.event.get():
			self.check_universal_events(pressed_keys, event)
			self.button.update(event)

			if event.type == KEYDOWN:
				if event.key == pygame.K_f:
					pygame.display.toggle_fullscreen()
				
				elif event.key == pygame.K_ESCAPE:
					self.game.scenes.pop()
					self.game.scenes[0].events = True
				
				elif event.key == pygame.K_LEFT:
					self.selected -= 1
					if self.selected < 0:
						self.selected = len(self.options)-1
					self.target_angle += self.section_arc
		
				elif event.key == pygame.K_RIGHT:
					self.selected += 1
					if self.selected > len(self.options)-1:
						self.selected = 0
					self.target_angle -= self.section_arc

		if self.rotation % 360 != self.target_angle % 360:
			self.rotate()
	
	def rotate(self):
		rotation_speed = 5
		if self.rotation < self.target_angle:
			self.rotation += rotation_speed
		elif self.rotation > self.target_angle:
			self.rotation -= rotation_speed

	def draw(self):
		self.button.draw()
		draw_text(self.game.screen, self.options[self.selected], (SCREEN_WIDTH//2+16, SCREEN_HEIGHT//2-222), 24)
		for i, icon in enumerate(self.icons):
			angle = self.rotation + (i * self.section_arc)
			#pygame.transform.rotate(icon, rotation_angle)
			angle_rad = math.radians(angle)
			x = self.menu_center[0] + self.section_radius * math.sin(angle_rad)
			y = self.menu_center[1] - self.section_radius * math.cos(angle_rad)
			self.game.screen.blit(icon, (x, y))

	def callback(self):
		print("callback")

