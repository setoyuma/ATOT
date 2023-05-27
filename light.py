import pygame as pg

from constants import *
from support import *

class Light:
    def __init__(self, position, radius, color, intensity):
        self.position = position
        self.radius = radius
        self.color = color
        self.intensity = intensity

    def generate_glow(self, number_of_lights, glow, radius) -> pg.Surface:
        surf = pg.Surface((radius*2, radius*2), pg.SRCALPHA)
        # pg.draw.rect(pg.display.get_surface(), "green", surf.get_rect())
        layers = 30

        glow = clamp(glow,0,255)
        for i in range(layers):
            k = i*glow
            k = clamp(k, 0, 255)
            pg.draw.circle(
                surf, (k,k,k), surf.get_rect().center, radius - i *3
            )

        return surf

    def apply_lighting(self, light_list, surface):
        overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA, 32)
        overlay.convert_alpha()
        overlay.fill((150,150,150,255))
        for light in light_list:
            overlay.blit(self.generate_glow(len(light_list), 15, self.radius*2), (light.rect.centerx-100, light.rect.centery-100), special_flags=pg.BLEND_RGB_ADD)
            
        surface.blit(overlay, (0,0), special_flags=pg.BLEND_RGB_MULT)