import pygame as pg

from constants import *
from support import *

class Light:
    def __init__(self, radius, color, intensity, manual_pos=(0,0)):
        self.position = pg.math.Vector2(manual_pos)
        self.radius = radius
        self.color = color
        self.intensity = intensity
        self.world_brightness = WORLD_BRIGHTNESS

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

    def apply_lighting(self, surface, light_source_list=None,):
        # create the overlay/world brightness
        overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA, 32)
        overlay.convert_alpha()
        overlay.fill((self.world_brightness,self.world_brightness,self.world_brightness))
        
        # if a manual position is set, blit a glow there
        if self.position.x > 0:
            overlay.blit(self.generate_glow(1, self.intensity, self.radius*2), (self.position.x-100, self.position.y-100), special_flags=pg.BLEND_RGB_ADD)
        else:
            # blit a glow at each light source in the list of lights
            for light_source in light_source_list:
                overlay.blit(self.generate_glow(len(light_source_list), self.intensity, self.radius*2), (light_source.rect.centerx-100, light_source.rect.centery-100), special_flags=pg.BLEND_RGB_ADD)
        
        # blit the overlay with the glows on the screen
        surface.blit(overlay, (0,0), special_flags=pg.BLEND_RGB_MULT)