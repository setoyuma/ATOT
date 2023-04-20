import pygame as pg
from settings import *


class UI:
    def __init__(self, surface):
        # setup
        self.display_surface = surface

        # health
        self.health_bar = pg.image.load(
            '../graphics/UI/HealthBar/HealthBar.png').convert_alpha()
        self.mana_bar = pg.image.load(
            '../graphics/UI/HealthBar/ManaBar.png').convert_alpha()
        self.scaled_health_bar = pg.transform.scale(self.health_bar, (98,98))
        self.scaled_mana_bar = pg.transform.scale(self.mana_bar, (98,98))
        self.health_bar_topleft = (0, 0)
        self.mana_bar_topleft = (100, 0)
        self.bar_max_width = 67
        self.bar_height = 46

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

        self.display_surface.blit(self.scaled_health_bar, self.health_bar_topleft)
    
    def show_mana(self, current, full):
        current_health_ratio = current / full
        current_bar_height = self.bar_height * current_health_ratio
        mana_bar_rect = pg.Rect(
            (self.mana_bar_topleft[0]+16, self.mana_bar_topleft[1]+49),
            (self.bar_max_width, current_bar_height)
            )
        pg.draw.rect(self.display_surface, 'red',
                     mana_bar_rect,
                     0,
                     0,
                     10,
                     10,
                     )

        self.display_surface.blit(self.scaled_mana_bar, self.mana_bar_topleft)

