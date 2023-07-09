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
	
	def universal_updates(self):
		self.game.cursor.update()

	def universal_draw(self):
		self.game.cursor.draw(self.game.screen)

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
		self.status = 'alpha'
		self.bg = scale_images([get_image('../assets/backgrounds/cavern1.png')], (1440, 1440))[0]
		self.game.screen = pygame.display.set_mode((1400,800))
		self.size = pygame.math.Vector2(800,800)
		# animation
		self.frame_index = 0
		self.animation_speed = 0.38
		self.import_assets()
		self.animation = self.animations[self.status]


		img = '../assets/ui/buttons/button_plate1.png'
		hover_img = '../assets/ui/buttons/button_plate2.png'
		self.buttons = [
			NewButton(self.game, (128,64), "new", (162, 655), self.load_new, img, hover_img, text_color=PANEL_COLOR, text_size=1),
			NewButton(self.game, (128,64), "play", (360, 655), self.load_world, img, hover_img, text_color=PANEL_COLOR, text_size=1)
		]

	def handle_buttons(self):
		# text
		for button in self.buttons:
			draw_custom_font_text(
				self.game.screen,
				self.game.alphabet,
				button.text,
				24,
				(button.rect.x + 18, button.rect.y + 18),
				[]					
				)

	def import_assets(self):
		self.animation_keys = {'alpha':[]} 

		for animation in self.animation_keys:
			full_path = LAUNCHER_ASSET_PATH + animation
			
			original_images = new_import_folder(full_path)
			scaled_images = scale_images(original_images, self.size)
			
			self.animation_keys[animation] = new_import_folder(full_path)

		self.animations = self.animation_keys
	
	def animate(self):
		animation = self.animation_keys[self.status]
		self.frame_index += self.animation_speed

		if self.frame_index >= len(animation):
			self.frame_index = self.frame_index - 1

		self.image = pygame.transform.scale(animation[int(self.frame_index)], self.size)

	def patch_notes(self):
		patch_notes_rect = pygame.Rect((100,150),(200,175))
		self.patch_plate = get_image('../assets/ui/menu/launcher/patch_notes_plate1.png')
		self.game.screen.blit(self.patch_plate, (8, 8))

		patch_notes = ['Launcher', 'Game']

		draw_custom_font_text(self.game.screen, self.game.alphabet, notes[patch_notes[0]], 42, (100,115), [' ', '.'])

	def draw_footer(self):
		savior_systems = scale_images([get_image('../assets/ss/logo.png')], (105, 103))[0]
		
		self.game.screen.blit(savior_systems, (1296, 695))

	def load_world(self):
		self.game.scenes = [WorldScene(self.game)]

	def load_new(self):
		self.game.scenes = [CreateNewGame(self.game)]

	def update(self):
		self.animate()
		self.universal_updates()
		pressed_keys = pygame.key.get_pressed()
		for event in pygame.event.get():
			self.check_universal_events(pressed_keys, event)
			# update
			for button in self.buttons:
				button.update(event)
			
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		
	def draw(self):
		self.game.screen.fill([0,0,0])
		self.game.screen.blit(self.bg, (0,0))
		self.game.screen.blit(self.image, (550,-50))
		# self.game.screen.blit(self.logo, (0,-200))
		self.patch_notes()

		# draw
		for button in self.buttons:
			button.draw()
			self.handle_buttons()

		self.draw_footer()
		self.universal_draw()


class CreateNewGame(Scene):
	
	def __init__(self, game):
		self.scene_type = 'create new'
		super().__init__(game)
		self.game.screen = pygame.display.set_mode((1400,800))
		self.buttons = []
		self.text_list = []
		self.particles = []
		self.letter_slots = []
		self.torch_rects = []
		self.name_length = ['','','','','','','','']
		self.layout_keyboard()
		self.handle_buttons()
		self.background = scale_images([get_image('../assets/ui/keyboards/alpha/alpha1.png')], self.game.screen.get_size())[0]

		# animation
		self.size = self.game.screen.get_size()
		self.status = 'alpha'
		self.frame_index = 0
		self.animation_speed = 0.1
		self.import_assets()
		self.animation = self.animations[self.status]

	def import_assets(self):
		self.animation_keys = {'alpha':[]} 

		for animation in self.animation_keys:
			full_path = KEYBOARD_BACKGROUNDS_SHORTCUT + animation
			
			original_images = new_import_folder(full_path)
			scaled_images = scale_images(original_images, self.size)
			
			self.animation_keys[animation] = new_import_folder(full_path)

		self.animations = self.animation_keys
	
	def animate(self):
		animation = self.animation_keys[self.status]
		self.frame_index += self.animation_speed

		if self.frame_index >= len(animation):
			self.frame_index = 0

		self.image = pygame.transform.scale(animation[int(self.frame_index)], self.size)

	def layout_keyboard(self):
		self.keyboard_rect = pygame.Rect((120, 360), (self.game.screen.get_width() - 245, self.game.screen.get_height() - 420))

		for index, slot in enumerate(self.name_length):
			self.letter_slots.append(
				pygame.Rect(
					(190 + 130 * index, 190),
					(96 , 160)
				)
			)
	
	def draw_letter(self):
		for button in self.buttons:
			if button.clicked:
				self.text_list.append(button.text)

		print(self.text_list)
		return(self.text_list)

	def handle_buttons(self):
		# text

		for index, letter in enumerate(self.game.alphabet):
			print(letter)
			img = self.game.font[index]

			if index in range(10, 18):
				row = (-600 + 96 * index, 455 + 100)
			elif index in range(18, 26):
				row = (-1368 + 96 * index, 455 + 200)
			else:
				row = (265 + 96 * index, 455)
			
			self.buttons.append(
				NewButton(
					self.game,
					96,
					letter, 
					row, 
					self.draw_letter,
					# base_color=[80,80,80],
					hover_color=[0,0,0],
					text_color=PANEL_COLOR, 
					text_size=1
					)
			)

	def handle_torches(self):
		torch_rect_2 = pygame.Rect((1304, 600), (96, 160))
		torch_rect_1 = pygame.Rect((0, 600), (96, 160))

		self.torch_rects = [
			torch_rect_1,
			torch_rect_2
		]

		img = scale_images([get_image('../assets/terrain/torch.png')], (160, 200))[0]

		# show torch rects
		# pygame.draw.rect(self.game.screen, 'blue', torch_rect_1)
		# pygame.draw.rect(self.game.screen, 'blue', torch_rect_2)

		for rect in self.torch_rects:
			for i in range(8):
				self.particles.append(
					Particle(
						self.game, 
						random.choice(seto_colors["torch1"]), 
						(rect.centerx + random.randint(-20,20), rect.centery - 84), 
						(0, random.randint(-4,-1)), 
						random.randint(2,8), 
						[],
						# glow=True,
						torch=True,
						# circle=True
						)
				)

		self.game.screen.blit(img, (torch_rect_1.x - 33, torch_rect_1.y))
		self.game.screen.blit(img, (torch_rect_2.x - 33, torch_rect_2.y))

	def draw(self):
		self.game.screen.fill([0,0,0])
		
		# show keyboard rect
		# surf = pygame.Surface((self.keyboard_rect.width, self.keyboard_rect.height))
		# surf.fill('green')
		# self.game.screen.blit(surf, (self.keyboard_rect.x, self.keyboard_rect.y))
		
		# keyboard background
		self.game.screen.blit(self.image, (0,-10))

		# button letters
		for button in self.buttons:
			button.draw()
			draw_custom_font_text(
				self.game.screen,
				self.game.alphabet,
				button.text,
				64,
				(button.rect.x + 18, button.rect.y + 8),
				[]					
			)

		# draw selected letters to screen
		for index, letter in enumerate(self.text_list):
			surf = scale_images([self.game.alphabet[letter]], (96,96))[0]
			if index + 1 <= len(self.name_length):
				self.game.screen.blit(surf, self.letter_slots[index].topleft)			
			else:
				self.text_list = self.text_list[:-1]


		# vfx
		self.handle_torches()
		for particle in self.particles:
			particle.emit()

			if particle.radius <= 0.1:
				self.particles.remove(particle)



		self.universal_draw()

	def update(self):
		self.animate()

		self.universal_updates()

		pressed_keys = pygame.key.get_pressed()
		for event in pygame.event.get():
			self.check_universal_events(pressed_keys, event)
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_BACKSPACE:
					print(self.text_list[:-1], 'result')
					self.text_list = self.text_list[:-1]

			for button in self.buttons:
				button.update(event)


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
			self.universal_updates()
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
					self.player.attack()

				# spells
				if event.key == pygame.K_p: #and self.player.collide_bottom:
					# add this once we have damage animations (and self.player.vulnerable)
					if self.player.facing_right  and self.player.magick > 0 and self.player.cast_timer == self.player.cast_cooldown:
						self.player.casting = True
						self.player.magick -= SPELLS[self.player.active_spell][3]
						self.player.projectiles.append(
							Projectile(self.game, (self.player.rect.right, self.player.rect.bottom - 50), self.player.active_spell, 'right', self.player.rect.center, 300)
						)
						play_sound(f'../assets/sounds/{self.player.active_spell}.wav')
					if not self.player.facing_right  and self.player.magick > 0 and self.player.cast_timer == self.player.cast_cooldown:
						self.player.casting = True
						self.player.magick -= SPELLS[self.player.active_spell][3]
						self.player.projectiles.append(
							Projectile(self.game, (self.player.rect.left, self.player.rect.bottom - 50), self.player.active_spell, 'left', self.player.rect.center, 300)
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

		# for enemy in self.world.enemies:
		# 	enemy.show_rects(self.game.screen)

		# self.game.player.show_rects(self.game.screen)
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

		self.universal_draw()


class RadialMenu(Scene):
	def __init__(self, game):
		super().__init__(game)
		self.scene_type = 'radial menu'
		self.menu_center = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
		self.icons = import_folder("../assets/ui/menu/radial")
		self.rotation = 0 # keep track of how much the menu has rotated
		self.target_angle = 0
		self.section_radius = 200  # distance from the center to each section
		self.sections = len(self.icons) # resume // settings // inventory // spells // equipment
		self.section_arc = 360 / self.sections
		self.button = NewButton(game, 32, "", (SCREEN_WIDTH//2+16, SCREEN_HEIGHT//2-184), self.callback, base=(0,0,100,50), hovered=(0,0,100,50))
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


	
