import pygame as pg
from settings import *
from support import *

class UI:
	def __init__(self, surface):
		# setup
		self.display_surface = surface

		# health
		self.health_bar = pg.image.load(
			'./assets/UI/HealthPot.png').convert_alpha()
		self.mana_bar = pg.image.load(
			'./assets/UI/ManaPot.png').convert_alpha()
		self.scaled_health_bar = pg.transform.scale(self.health_bar, (98, 98))
		self.scaled_mana_bar = pg.transform.scale(self.mana_bar, (98, 98))
		self.health_bar_topleft = (0, 0)
		self.mana_bar_topleft = (100, 0)
		self.bar_max_width = 67
		self.bar_height = 46

		# mini map
		mini_map = get_image('./assets/UI/maps/Mini_Map.png')
		self.scaled_mini_map = pg.transform.scale(mini_map, (350,350))

	def draw_mini_map(self, player_stats):
		self.display_surface.blit(self.scaled_mini_map, (SCREEN_WIDTH-345, SCREEN_HEIGHT - 750))
		
		draw_text(self.display_surface, f"STR | {player_stats['str']}", (1185, 210), 20, (255,255,255))
		draw_text(self.display_surface, f"MGCK | {player_stats['mgck']}", (1185, 240), 20, (255,255,255))
		draw_text(self.display_surface, f"HP | {player_stats['hp']}", (1075, 210), 20, (255,255,255))
		draw_text(self.display_surface, f"DEF | {player_stats['def']}", (1075, 240), 20, (255,255,255))
		draw_text(self.display_surface, f"XP | {player_stats['xp']}", (1080, 270), 20, (255,255,255))
		draw_text(self.display_surface, f"ORBS | {player_stats['xporb']}", (1175, 270), 20, (255,255,255))

	def show_health(self, current, full):
		current_health_ratio = current / full
		current_bar_height = self.bar_height * current_health_ratio
		health_bar_rect = pg.Rect(
			(self.health_bar_topleft[0]+16, self.health_bar_topleft[1]+49),
			(self.bar_max_width, current_bar_height)
		)
		pg.draw.rect(self.display_surface, 'red',
					 health_bar_rect,
					 0,
					 0,
					 10,
					 10,
					 )

		self.display_surface.blit(
			self.scaled_health_bar, self.health_bar_topleft)

	def show_mana(self, current, full):
		current_health_ratio = current / full
		current_bar_height = self.bar_height * current_health_ratio
		mana_bar_rect = pg.Rect(
			(self.mana_bar_topleft[0]+16, self.mana_bar_topleft[1]+49),
			(self.bar_max_width, current_bar_height)
		)
		pg.draw.rect(self.display_surface, 'teal',
					 mana_bar_rect,
					 0,
					 0,
					 10,
					 10,
					 )

		self.display_surface.blit(self.scaled_mana_bar, self.mana_bar_topleft)
