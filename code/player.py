import pygame as pg
from settings import *
from support import *


class Player(pg.sprite.Sprite):
    def __init__(self, pos, groups, collisionSprites, surface):
        super().__init__(groups)
        self.import_character_assets()
        self.image = pg.Surface((TILE_SIZE//2, TILE_SIZE))
        self.frame_index = 0
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.spawnx = pos[0]
        self.spawny = pos[1]
        self.display_surface = surface

        # self stats
        self.hp = 100
        self.mana = 100
        self.hitStatus = False
        self.invincible = False
        self.invincibilityDuration = 800
        self.hurtTime = 0
        self.attackActive = 1.2
        self.attackDuration = 0

        # self state
        self.animation_speed = 0.20
        self.status = 'idle'
        self.on_left = False
        self.on_right = False
        self.hitBoxOn = False
        self.currentX = None
        self.wallJump = False
        self.attacking = False

        # self movement
        self.direction = pg.math.Vector2()
        self.speed = 7
        self.gravity = 0.85
        self.jumpHeight = 16  # jump speed
        self.collisionSprites = collisionSprites
        self.onGround = False
        self.onCeiling = False
        self.facing_right = True
        self.airBorne = False
        self.wallJumpCounter = 1

    def import_character_assets(self):
        character_path = '../graphics/character/'
        self.animations = {'idle': [], 'run': [],
                           'jump': [], 'fall': [], 'attack': [], }

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self):
        animation = self.animations[self.status]
        self.hitBox = pg.rect.Rect(self.rect.x, self.rect.y, 15, 60)
        self.hitBox.center = self.rect.center
        # loop over frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if self.facing_right:
            scaled_image = pg.transform.scale(image, (64,64))
            self.image = scaled_image
        else:
            scaled_image = pg.transform.scale(image, (64,64))
            flipped_image = pg.transform.flip(scaled_image, True, False)
            self.image = flipped_image

            # set the rect
        if self.onGround and self.on_right:
            self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
        elif self.onGround and self.on_left:
            self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        elif self.onGround:
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        elif self.onCeiling and self.on_right:
            self.rect = self.image.get_rect(topright=self.rect.topright)
        elif self.onCeiling and self.on_left:
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
        elif self.onCeiling:
            self.rect = self.image.get_rect(midtop=self.rect.midtop)

    def get_status(self):
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1 and self.onGround == False:
            self.status = 'fall'
        elif self.direction.x != 0 and self.onGround:
            self.status = 'run'
        else:
            if self.direction.y == 0 and self.onGround:
                self.status = 'idle'

        if self.onGround:
            self.airBorne = False
        else:
            self.airBorne = True

        if self.attacking:
            self.status = 'attack'

    def input(self):
        keys = pg.key.get_pressed()

        if keys[pg.K_d]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pg.K_a]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        if keys[pg.K_SPACE] and self.onGround:
            self.direction.y = -self.jumpHeight

        if keys[pg.K_p] and self.onGround:
            self.attacking = True
        # else:
            # self.attacking = False

    def horizontalCollisions(self):
        for sprite in self.collisionSprites.sprites():
            if sprite.rect.colliderect(self.rect):
                if self.direction.x < 0:
                    self.rect.left = sprite.rect.right
                    self.on_left = True
                    self.currentX = self.rect.left
                    # print(f'touching left: {self.on_left}')

                if self.direction.x > 0:
                    self.rect.right = sprite.rect.left
                    self.on_right = True
                    self.currentX = self.rect.right
                    # print(f'touching right: {self.on_right}')
        if self.on_left and (self.rect.left < self.currentX or self.direction.x >= 0):
            self.on_left = False
        if self.on_right and (self.rect.right > self.currentX or self.direction.x <= 0):
            self.on_right = False

    def verticalCollisions(self):
        for sprite in self.collisionSprites.sprites():
            if sprite.rect.colliderect(self.rect):
                if self.direction.y > 0:
                    self.rect.bottom = sprite.rect.top
                    self.direction.y = 0
                    self.onGround = True
                if self.direction.y < 0:
                    self.rect.top = sprite.rect.bottom
                    self.direction.y = 0
                    self.onCeiling = True

            # if self.onGround and self.direction.y != 0:
            #     self.onGround = False

        if self.onGround and self.direction.y < 0 or self.direction.y > 1:
            self.onGround = False
        if self.onCeiling and self.direction.y > 0.1:
            self.onCeiling = False

    def applyGravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def attack(self):
        if self.attacking:
            self.attackActive = pg.time.get_ticks()

    def getDamage(self):
        if not self.invincible:
            if self.hp > 0:
                self.hp -= 10
                self.invincible = True
                self.hurtTime = pg.time.get_ticks()
            else:
                print("dead, resart level")

    def iFrameTimer(self):
        if self.invincible:
            currentTime = pg.time.get_ticks()
            if currentTime - self.hurtTime >= self.invincibilityDuration:
                self.invincible = False

    def attackTimer(self):
        if self.attacking:
            currentTime = pg.time.get_ticks()
            if currentTime - self.attackActive >= self.attackDuration:
                self.attacking = False

    def update(self):

        self.input()
        self.rect.x += self.direction.x * self.speed
        self.horizontalCollisions()
        self.applyGravity()
        self.verticalCollisions()

        self.get_status()
        self.animate()
        self.iFrameTimer()
        self.attackTimer()

        pg.draw.rect(self.display_surface, "blue", self.hitBox)
        # pg.draw.rect(self.display_surface, "red", self.rect)
