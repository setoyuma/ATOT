from BLACKFORGE2DEV import *
from CONSTANTS import *
from entities import *

class Camera():
	def __init__(self, game, scroll_speed:int, interpolation:int):
		self.game = game
		self.level_scroll = pygame.math.Vector2()
		self.scroll_speed = scroll_speed
		self.interpolation = interpolation
		self.shake = False
		self.shake_timer = 0

	def horizontal_scroll(self):
		self.level_scroll.x += ((self.game.world.player.rect.centerx - self.level_scroll.x - (HALF_WIDTH - self.game.world.player.size.x + 150)) / self.interpolation * self.scroll_speed) * self.game.dt

	def vertical_scroll(self):
		self.level_scroll.y += (((self.game.world.player.rect.centery - 180) - self.level_scroll.y - (HALF_HEIGHT - self.game.world.player.size.y + 120)) / self.interpolation * self.scroll_speed) * self.game.dt

	def hit_shake(self):
		if self.shake_timer > 0 and self.shake:
			# if sine_wave_value() > 0:
			self.level_scroll.x += (random.randint(-100, 100) / self.interpolation * self.scroll_speed) * self.game.dt

	def update_position(self):
		self.horizontal_scroll()
		self.vertical_scroll()
		self.hit_shake()


		# constrain camera velocity
		if self.game.world.level_topleft.left + self.level_scroll.x < 0:
			self.level_scroll.x = 0
		elif self.game.world.level_bottomright.right - self.level_scroll.x < SCREEN_WIDTH:
			self.level_scroll.x = self.game.world.level_width - SCREEN_WIDTH
		
		if self.game.world.level_topleft.top - self.level_scroll.y > 0:
			self.level_scroll.y = 0
		elif self.game.world.level_bottomright.bottom - self.level_scroll.y < SCREEN_HEIGHT:
			self.level_scroll.y = self.game.world.level_height - SCREEN_HEIGHT

		if self.shake_timer != 0:
			self.shake_timer -= 1 * self.game.dt
		if self.shake_timer < 0:
			self.shake_timer = 0
			self.shake = False


class HUD:
	def __init__(self, game, player, surface):
		self.game = game
		self.player = player
		self.display = surface

		self.player_hud = get_image('../assets/ui/HUD/HUD.png')
		self.player_portrait = get_image('../assets/ui/HUD/alryn_faceset2.png')
		self.player_hud = scale_images([self.player_hud], (460,127))[0]
		self.player_portrait = scale_images([self.player_portrait], (87,81))[0]

	def update_spell_shard_count(self):
		spell_shard_img = get_image('../assets/items/magick/magick_shard/magick_shard1.png')
		self.display.blit(spell_shard_img, (40, 120))
		draw_text(self.display, f"{self.player.magick_shards}", [25, 150], size=32)

	def update_spell_slot(self):
		self.spell_1_image = get_image(SPELL_PATH+self.player.active_spell+'/'+self.player.active_spell+'1'+'.png')
		self.spell_1_image = scale_images([self.spell_1_image], (96,96))
		self.spell_1_image = self.spell_1_image[0]
		spell_slot_1_rect = pygame.Rect((1, SCREEN_HEIGHT - 121), (96,96))
		self.display.blit(self.spell_1_image, spell_slot_1_rect)

	def update_player_HUD(self):
		# under bars
		self.health_under_bar = pygame.Rect((98, 62), (364, 26))
		self.magick_under_bar = pygame.Rect((98, 78), (364, 26))
		# bars
		self.health_bar = pygame.Rect((98, 62), (364 * self.player.health/self.player.health_scale, 26))
		self.magick_bar = pygame.Rect((90, 90), (374 * self.player.magick/self.player.magick_scale, 14))
		
		pygame.draw.rect(self.display, [0,0,0], self.health_under_bar)
		pygame.draw.rect(self.display, [0,0,0], self.magick_under_bar)
		pygame.draw.rect(self.display, [150,0,0], self.health_bar)
		pygame.draw.rect(self.display, [0,150,200], self.magick_bar)
		self.display.blit(self.player_hud, (5,10))
		# self.display.blit(self.player_portrait, (25,10))
		
		if self.player.spell_shards > 0:
			spell_shard_1 = pygame.transform.scale(get_image('../assets/UI/HUD/HUD_SHARD.png'), (54, 30))
			self.display.blit(spell_shard_1, (105, 35))
		
		if self.player.spell_shards == 2:
			spell_shard_2 = pygame.transform.scale(get_image('../assets/UI/HUD/HUD_SHARD.png'), (54, 30))
			self.display.blit(spell_shard_2, (136, 35))
