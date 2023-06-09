from saviorsystems.REDFORGE import *

from game_data import levels
from level import Level

from CONSTANTS import *

from projectile import Projectile


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
		self.logo = get_image("../assets/ui/abberoth.png")
		self.game.screen = pygame.display.set_mode((1000,600))
		img = '../assets/ui/buttons/button_plate1.png'
		self.buttons = [
			Button(game, "NEW", (925, 355), None, img, img),
			Button(game, "PLAY", (925, 455), self.load_world, img, img),
			#Button(game, "QUIT", (self.game.settings["screen_width"] - 100, 50,), pygame.quit, img, img)
		]
		# if self.game.loaded_data is not None:
		# 	self.buttons.append(Button(game, "PLAY", (925, 455), self.load_world, img, img))
		
	def patch_notes(self):
		patch_notes_surf = pygame.Surface((240,250))
		patch_notes_surf.fill("white")
		self.game.screen.blit(patch_notes_surf, (10,125))
		patch_notes_rect = patch_notes_surf.get_rect(topleft=(10,175))
		# pygame.draw.rect(self.screen, "red", patch_notes_rect)
		draw_text(self.game.screen, "Patch Notes", (120,150), color="black")
		text_line_wrap(self.game.screen, f"{notes['Launcher']}"+f"{notes['Game']}", "black", patch_notes_rect, pygame.font.Font(None, 30), aa=True)

	def load_world(self):
		self.game.scenes = [WorldScene(self.game, levels[self.game.current_level])]

	def update(self):
		# input_handler.update()

		for event in pygame.event.get():
			for button in self.buttons:
				button.update(event)

			if event.type == pygame.QUIT:
				print("Game Closed")
				pygame.quit()
				sys.exit()

	def draw(self):
		self.game.screen.fill("black")
		self.game.screen.blit(self.logo, (0,0))
		
		self.patch_notes()

		for button in self.buttons:
			button.draw()

		self.game.draw_fps()
class WorldScene(Scene):
	def __init__(self, game, level_data):
		super().__init__(game)
		self.game.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SCALED)
		self.game.level = Level(self.game, level_data, self.game.screen)
		self.game.player = self.game.level.player
		self.game.projectiles = []
		self.events = True
		# pygame.display.toggle_fullscreen()

	def update(self):
		if not self.events:
			return

		pressed_keys = pygame.key.get_pressed()		
		for event in pygame.event.get():
			self.check_universal_events(pressed_keys, event)
			# handle player input
			self.game.player.get_input()

			if event.type == pygame.QUIT:
				print("Game Closed")
				pygame.quit()
				sys.exit()

			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					self.game.projectiles.append(
						Projectile(
							"fireball",  #type can be any spell in ../assets/spells/
							self.game.player.rect.center,
							48,
							10, 
							10, 
							self.game.level.terrain, 
							self.game.level.projectiles, 
							self.game.level.world_shift
							)
					)
				# if event.button == 4:
				# 	print("mouse up")
				# 	self.game.level.camera.zoom += 0.1
				# if event.button == 5:
				# 	print("mouse down")
				# 	self.game.level.camera.zoom -= 0.1
				# if event.button == 1:
				# 	level = self.game.level
				pass

			elif event.type == pygame.MOUSEBUTTONUP:
				pass

			elif event.type == KEYDOWN:
				if event.key == pygame.K_f:
					pygame.display.toggle_fullscreen()

				elif event.key == pygame.K_ESCAPE:
					if len(self.game.scenes) == 1:
						self.game.scenes.append(RadialMenu(self.game))
						self.events = False
		""" LEVEL CHANGING """
		# print(f"next room triggered: {self.game.level.next_room_triggered}")
		# print(f"last room triggered from scenes: {self.game.level.last_room_triggered}")
		if self.game.level.next_room_triggered:
			self.game.current_level += 1
			self.game.scenes = [WorldScene(self.game, levels[self.game.current_level])]
		
		if self.game.level.last_room_triggered:
			self.game.current_level -= 1
			self.game.scenes = [WorldScene(self.game, levels[self.game.current_level])]

	def draw(self):
		self.game.screen.fill("black")
		self.game.level.run()

class RadialMenu(Scene):
	def __init__(self, game):
		super().__init__(game)
		self.menu_center = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
		self.icons = import_folder("../assets/ui/menu/")
		self.rotation = 0 # keep track of how much the menu has rotated
		self.target_angle = 0
		self.section_radius = 200  # distance from the center to each section
		self.sections = len(self.icons)
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
					play_sound("../assets/sounds/menu_select.wav")
		
				elif event.key == pygame.K_RIGHT:
					self.selected += 1
					if self.selected > len(self.options)-1:
						self.selected = 0
					self.target_angle -= self.section_arc
					play_sound("../assets/sounds/menu_select.wav")

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
			angle_rad = math.radians(angle)
			x = self.menu_center[0] + self.section_radius * math.sin(angle_rad)
			y = self.menu_center[1] - self.section_radius * math.cos(angle_rad)
			self.game.screen.blit(icon, (x, y))

	def callback(self):
		print("callback")

