import pygame as pg
from support import draw_text


class StatLine():
    def __init__(self, text, size, player, location, color, surf):
        self.text = text
        self.x = location[0]
        self.y = location[1]
        self.size = size
        self.player = player
        self.color = color
        self.display_surface = surf
        self.hp_bar = pg.Rect(self.x-68, self.y, 100, 10)


    def draw(self):

        draw_text(self.display_surface, f"{self.player.get_player(self.player.player_name)['Rank']}", (self.x-18, self.y-15), self.size, self.color, "black")
        # draw_text(self.display_surface, f"Xp: {self.player.player_stat_sheet['XP']}", (self.x, self.y+20), self.size, self.color, "gray")

        pg.draw.rect(self.display_surface, "lime", self.hp_bar)


    def update(self):
        self.draw()