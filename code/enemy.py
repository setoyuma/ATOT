import pygame as pg
from tile import AnimatedTile
from random import randint


class Enemy(AnimatedTile):
    def __init__(self, size, x, y, groups, enemy_type):
        super().__init__(size, x, y, groups,
                         f'../graphics/enemy/{enemy_type}/run')
        self.rect.y += size - self.image.get_size()[1]

        self.image = pg.transform.scale(self.image, (64,64))
        if enemy_type == 'caim':
            self.speed = 5

        if enemy_type == 'ferrigus':
            self.speed = 3

    def move(self):
        self.rect.x += self.speed

    def reverse_image(self):
        if self.speed < 0:
            self.image = pg.transform.flip(self.image, True, False)

    def reverse(self):
        self.speed *= -1

    def update(self):
        self.animate()
        self.move()
        self.reverse_image()
