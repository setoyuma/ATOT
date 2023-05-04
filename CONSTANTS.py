notes = {
	"Launcher" : "Added patch notes section, and character list.",
	"Game" : "Added decoration tiles and level system."
}

TILE_SIZE = 64
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 720
BASE_SPEED = 5
ENEMY_SPEED = 3
bullet_speed = 5

# colors
BG_COLOR = '#060C17'
PLAYER_COLOR = '#C4F7FF'
TILE_COLOR = '#94D7F2'

projectile_types = {
	1: "windblade",
	2: "iceorb",
	3: "fireball",
}

ranks = {
	"Civilian": 25,
	"Page": 50,
	"Squire": 75,
	"Knight": 100,
	"Mage": 125,
	"Oracle": 150,
	"Spellweaver": 175,
	"Lord": 200,
	"Voidtouched": 225,
	"Shaper": 250,
}

world_0 = {
    'player': './assets/world/level_data/data/Abberoth_player.csv',
    'ground': './assets/world/level_data/data/Abberoth_ground.csv',
    'terrain': './assets/world/level_data/data/Abberoth_terrain.csv',
    'foreground': './assets/world/level_data/data/Abberoth_foreground.csv',
    'constraint': './assets/world/level_data/data/Abberoth_constraint.csv',
}

worlds = {
    1: world_0
}
