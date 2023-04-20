import pygame as pg
from settings import *
from tile import Tile, StaticTile, DecorationTile, AnimatedTile
from player import Player
from support import *
from ui import UI
from camera import CameraGroup
from enemy import Enemy


class Level:

    def __init__(self, level_data, game_clock):
        # level setup
        self.displaySurface = pg.display.get_surface()

        #game clock
        self.gameClock = game_clock

        # ui
        self.UI = UI(self.displaySurface)

        # sprite group setup
        self.visibleSprites = CameraGroup()  # sprites here will be drawn
        self.activeSprites = pg.sprite.Group()  # sprites in here will be updated
        # sprites that the player can collide with
        self.collisionSprites = pg.sprite.Group()

        # terrain layout
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(
            terrain_layout, 'terrain')
        
        '''ANIM TILES'''
        # elwyr-floor layout
        elwyr_floor_layout = import_csv_layout(level_data['elwyr-floor'])
        self.elwyr_floor_sprites = self.create_tile_group(
            elwyr_floor_layout, 'elwyr-floor')

        # constraints
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(
            constraint_layout, 'constraints')
        
        # grass
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(
          grass_layout, 'grass')
        
        # event-tile
        event_tile_layout = import_csv_layout(level_data['events'])
        self.event_tile_sprites = self.create_tile_group(
          event_tile_layout, 'events')

        # decorations
        decoration_layout = import_csv_layout(level_data['decoration'])
        self.decoration_sprites = self.create_tile_group(
            decoration_layout, 'decoration')

        # player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

        # enemy
        enemy_layout = import_csv_layout(level_data['enemy'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemy')

    def enemyPlayerCollision(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.Rect.colliderect(enemy.rect, self.Player.hitBox):
                print('player touched enemy')
                self.Player.getDamage()

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()

    def eventTileCheck(self,target):
        if pg.sprite.spritecollide(self.player.sprite, self.event_tile_sprites, False):
            print('event triggered');
            # while event: 

    def create_tile_group(self, layout, type):
        sprite_group = pg.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics(
                            '../levels/tilesets/Static_Tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(TILE_SIZE, x, y, tile_surface, [
                                            self.visibleSprites, self.collisionSprites])
                    if type == 'constraints':
                        sprite = Tile(TILE_SIZE, x, y, [self.activeSprites])
                    
                    if type == 'decoration':
                        decoration_tile_list = import_cut_graphics(
                            '../graphics/decoration/decorations.png')
                        decoration_surface = decoration_tile_list[int(val)]
                        sprite = DecorationTile(TILE_SIZE, x, y, decoration_surface, [
                                            self.visibleSprites, self.activeSprites])
                    if type == 'enemy':
                        sprite = Enemy(TILE_SIZE, x, y, [
                                       self.activeSprites, self.visibleSprites], 'ferrigus')
                    
                    if type == 'grass':
                        sprite = AnimatedTile(TILE_SIZE, x, y, [self.visibleSprites,self.activeSprites], '../graphics/decoration/grass/')
                    
                    if type == 'events':
                        sprite = Tile(TILE_SIZE, x, y, [self.activeSprites])
                   
                    if type == 'elwyr-floor':
                        sprite = AnimatedTile(TILE_SIZE, x, y, [self.visibleSprites,self.activeSprites, self.collisionSprites], '../graphics/terrain/anim-tiles/elwyr-floor/')

                        

                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if val == '0':
                    # print(f"Proper Spawn x: {x}")
                    # print(f"Proper Spawn y: {y}")
                    self.Player = Player((x, y), [
                                         self.visibleSprites, self.activeSprites], self.collisionSprites, self.displaySurface)
                    self.player.add(self.Player)
                    self.visibleSprites.add(self.Player)
                if val == '1':
                    pass
                    # hat_surface = pygame.image.load(
                    #     '../graphics/character/hat.png').convert_alpha()
                    # sprite = Tile((x, y), [self.activeSprites])
                    # self.goal.add(sprite)

    def run(self):
        # run the game(level)
        self.grass_sprites.update()
        self.player.update()
        self.enemy_sprites.update()
        self.event_tile_sprites.update()
        self.elwyr_floor_sprites.update()
        self.constraint_sprites.update()
        self.visibleSprites.customDraw(self.Player)
        self.enemyPlayerCollision()
        self.enemy_collision_reverse()
        self.eventTileCheck(self.Player)

        # ui
        self.UI.show_health(self.Player.hp, 100)
        self.UI.show_mana(self.Player.mana, 100)

