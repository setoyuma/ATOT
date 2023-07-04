import random, time

from world_data import worlds
from BLACKFORGE2 import *
from CONSTANTS import *
from projectile import *
from particle import *
from entities import *
from scenes import *
from utils import *


class Camera:
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


class UI:
	HUD_PATH = '../assets/ui/HUD/HUD.png'
	PORTRAIT_PATH = '../assets/ui/HUD/alryn_faceset2.png'
	
	def __init__(self, game, surface):
		self.game = game
		self.display = surface
		self.player_hud = self.load_and_scale_image(self.HUD_PATH, (460,100))
		self.player_portrait = self.load_and_scale_image(self.PORTRAIT_PATH, (87,81))

	def load_and_scale_image(self, path, size):
		return scale_images([get_image(path)], size)[0]

	def update_player_HUD(self):
		# under bars
		self.draw_under_bars()
		# bars
		self.draw_bars()
		# HUD and portrait
		self.display.blit(self.player_hud, (5,10))
		self.display.blit(self.player_portrait, (25,10))
		# shards
		self.draw_shards()

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

	def draw_under_bars(self):
		self.health_under_bar = pygame.Rect((98, 60), (364, 26))
		self.magick_under_bar = pygame.Rect((98, 78), (364, 26))
		pygame.draw.rect(self.display, [0,0,0], self.health_under_bar)
		pygame.draw.rect(self.display, [0,0,0], self.magick_under_bar)
	
	def draw_bars(self):
		self.health_bar = pygame.Rect((98, 60), (364 * self.game.player.health/self.game.player.health_scale, 26))
		self.magick_bar = pygame.Rect((90, 90), (374 * self.game.player.magick/self.game.player.magick_scale, 14))
		pygame.draw.rect(self.display, [150,0,0], self.health_bar)
		pygame.draw.rect(self.display, [0,150,200], self.magick_bar)

	def draw_shards(self):
		if self.game.player.spell_shards > 0:
			spell_shard_1 = pygame.transform.scale(get_image('../assets/UI/HUD/HUD_SHARD.png'), (54, 30))
			self.display.blit(spell_shard_1, (105, 35))
		if self.game.player.spell_shards == 2:
			spell_shard_2 = pygame.transform.scale(get_image('../assets/UI/HUD/HUD_SHARD.png'), (54, 30))
			self.display.blit(spell_shard_2, (136, 35))


class Game:
	def __init__(self):
		self.setup_pygame()
		self.setup_world()

		self.particle_presets = {
			# "torch": Particle(self, random.choice(seto_colors), ((mx + random.randint(-20, 20)) + self.camera.level_scroll.x, my + random.randint(-20, 20) + self.camera.level_scroll.y), (0, -4), 3, [pygame.sprite.Group()]),
		}

		self.mouse_particles = []

	def setup_pygame(self):
		self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SCALED)
		self.scaled_display = pygame.Surface((SCREEN_SIZE[0]//3, SCREEN_SIZE[1]//3))
		self.clock = pygame.time.Clock()
		pygame.display.set_caption("A Tale Of Time")
		pygame.display.set_icon(get_image('../assets/logo.ico'))

	def setup_world(self):
		self.world_brightness = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
		self.world_brightness.convert_alpha()
		self.enemy_sprites = pygame.sprite.Group()
		self.current_world = 1
		self.world = World(self, worlds[self.current_world])

		# create player
		self.player_sprite_group = pygame.sprite.GroupSingle()
		self.player = Player(self, "ALRYN", 96, self.world.player_spawn, CHARACTERS["ALRYN"]["SPEED"], [self.player_sprite_group])

		# create camera
		self.camera = Camera(self, 10, 250)
		
		# ui
		self.ui = UI(self, self.screen)

		# item test
		self.item_group = pygame.sprite.Group()

		self.full_background = scale_images([
			get_image('../assets/background.png'),
			get_image('../assets/midground.png'),
			get_image('../assets/foreground.png')
		], (self.world.level_width, self.world.level_height))

	def draw_background(self):
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
			if event.type == pygame.QUIT:
				self.running = False

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_f:
					pygame.display.toggle_fullscreen()
			
			self.player.handle_event(event)

	def update(self):
		self.dt = time.time() - self.last_time  # calculate the time difference
		self.dt *= FPS_SCALE   # scale the dt by the target framerate for consistency
		self.last_time = time.time()  # reset the last_time with the current time
		self.current_fps = self.clock.get_fps()

		self.handle_events()
		self.world.update()
		self.world.update_enemies(self.dt, self.screen, self.world.tile_rects, self.world.constraint_rects)
		self.player.update(self.dt, self.screen, self.world.tile_rects)
		self.camera.update_position()

	def draw(self):
		self.draw_background()
		self.world.draw_world(self.screen)
		self.player.stat_bar()
		self.ui.update_player_HUD()
		self.ui.update_spell_slot()
		self.ui.update_spell_shard_count()
		self.world.update_items(self.screen)

	def handle_projectiles(self):
		for projectile in self.player.projectiles:
			projectile.draw(self.screen)

			if projectile.status == 'remove':
				self.player.projectiles.remove(projectile)
			else:
				if projectile.position.x >= projectile.cast_from.x + projectile.distance:
					projectile.status = 'hit'				
				if projectile.position.x <= projectile.cast_from.x - projectile.distance:
					projectile.status = 'hit'

	def handle_weapons(self):
		if len(self.player.weapon) > 0:
			for weapon in self.player.weapon:
				weapon.draw(self.screen)

				if not self.player.attacking:
					self.player.weapon.remove(weapon)

	def run(self):
		self.running = True
		self.last_time = time.time()
		while self.running:
			self.update()
			self.draw()
			self.handle_projectiles()
			self.handle_weapons()
			self.draw_fps()
			self.send_frame()


if __name__ == "__main__":
	game = Game()
	game.run()
