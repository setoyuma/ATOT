from BLACKFORGE2DEV import *


notes = {
	"Launcher" : "ABBEROTH",
	"Game" : "Added decoration tiles and level system."
}

FPS_SCALE = 75.0
FPS = 75
# FPS = 25
# FPS = 10

default_controls = {
    'menu': pygame.K_ESCAPE,
    'fullscreen': pygame.K_F11,
	'show fps': pygame.K_F8,
    'move_left': pygame.K_a,
    'move_right': pygame.K_d,
    'dash/roll': pygame.K_LSHIFT,
    'melee': 1,
    'cast': 3,
    'cycle up': 4,
    'cycle down': 5,
}

# Custom controls
custom_controls = default_controls.copy()

key_shortcuts = {
	'a': pygame.K_a,
	'b': pygame.K_b,
	'c': pygame.K_c,
	'd': pygame.K_d,
	'e': pygame.K_e,
	'f': pygame.K_f,
	'g': pygame.K_g,
	'h': pygame.K_h,
	'i': pygame.K_i,
	'j': pygame.K_j,
	'k': pygame.K_k,
	'l': pygame.K_l,
	'm': pygame.K_m,
	'n': pygame.K_n,
	'o': pygame.K_o,
	'p': pygame.K_p,
	'q': pygame.K_q,
	'r': pygame.K_r,
	's': pygame.K_s,
	't': pygame.K_t,
	'u': pygame.K_u,
	'v': pygame.K_v,
	'w': pygame.K_w,
	'x': pygame.K_x,
	'y': pygame.K_y,
	'z': pygame.K_z,
	'left click': 1,
	'right click': 2,
}


2.7 # chunks visible on screen on x axis -> SCREEN_WIDTH / ( chunk_size * TILE_SIZE)
1.5 # chunks visible on screen on y axis -> SCREEN_HEIGHT / ( chunk_size * TILE_SIZE)

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

HALF_WIDTH = SCREEN_WIDTH // 2
HALF_HEIGHT = SCREEN_HEIGHT // 2
CENTER = (HALF_WIDTH, HALF_HEIGHT)

# world
TILE_SIZE = 64
WORLD_BRIGHTNESS = 170
TORCH_BRIGHTNESS = 180
GRAVITY = 0.6
CHUNK_SIZE = 8

# path shortcuts
CHAR_PATH = '../assets/character/'
SPELL_PATH = '../assets/spells/' 
HITSPARK_PATH = '../assets/spells/hitsparks/' 
ENEMY_PATH = '../assets/enemy/'
ITEMS_PATH = '../assets/items/'
LAUNCHER_ASSET_PATH = '../assets/ui/menu/launcher/'
KEYBOARD_BACKGROUNDS_SHORTCUT = '../assets/ui/keyboards/'
MAIN_MENU_SHORTCUT = '../assets/ui/menu/main_menu/'

# colors 
BG_COLOR = '#060C17'
PLAYER_COLOR = '#C4F7FF'
TILE_COLOR = '#94D7F2'
PANEL_COLOR = [232, 157, 85]
ALRYN_COLORS = {
	'blue': [52, 0, 11],
	'blue shadows': [28, 0, 52],
	'gold': [197, 130, 0],
	'skin': [108, 130, 141],
	'skin shadows':	[72, 90, 97],
	'hair': [255, 255, 255],
	'hair shadows': [182, 182, 182],
}


seto_colors = {
	"torch1": {
		0: [185, 60, 60], # orange
		1: [255, 0, 0], # red
		2: [250, 250, 0], # yellow
		3: [80, 50, 50], # brown
	}
}

""" WORLD DATA """
WORLDS = {
	'church_of_melara':{
		'csv': {
			'terrain': '../levels/church_of_melara2/church_of_melara2_terrain.csv',
			'player': '../levels/church_of_melara2/church_of_melara2_player.csv',
			'enemy': '../levels/church_of_melara2/church_of_melara2_enemy.csv',
			'torch': '../levels/church_of_melara2/church_of_melara2_torch.csv',
			'foreground': '../levels/church_of_melara2/church_of_melara2_foreground.csv',
			'midground': '../levels/church_of_melara2/church_of_melara2_midground.csv',
			'background': '../levels/church_of_melara2/church_of_melara2_background.csv',
		},
		'music': ['FrozenWinds']

	},
	'test map': {
		'csv': {
			'terrain': '../levels/test_map/test_map_terrain.csv',
			'player': '../levels/test_map/test_map_player.csv',
			'torch': '../levels/test_map/test_map_torch.csv',
			'foreground': '../levels/test_map/test_map_foreground.csv',
			'enemy': '../levels/test_map/test_map_enemy.csv',
		},
		'music': ['FrozenWinds']
	}
}


""" CHARACTER STATS """
CHARACTERS = {
	"ALRYN": {
		"SPRITE SIZE": 160,
		"NAME": "Alryn",
		"HEALTH": 100,
		"MAGICK": 120,
		"SPEED": 5.5,
		"JUMPS": 1,
		"JUMPFORCE": 16.2,
		"ROLL SPEED": 8,
		"ROLL COOLDOWN": 4,
		"ATK_CD": 320,
		"CAST_CD": 50,
		"DASH DIST": 30,
		"ROLL DIST": 2,
		"IFRAMES": 300,

		"hitboxes": {
			"overhead1": [4, (-60, 50, 40, 50)],
			# "overhead2": [4, (-60, 50, 40, 50)],
		}
	}
}

ENEMIES = {
	"rose_sentinel": {
		"SPRITE SIZE": 96,
		"NAME": 'Rose Sentinel',
		"HEALTH": 25,
		"EXP": 3,
		'DAMAGE': 8,
		"ATTACK_TYPE": 'evergreen_serpent',
		"SPEED": 2,
		"RESIST": 1,
		"ATK_CD": 400,
		"IFRAMES": 300,
		"ATK_RAD": 200,
		"AGR_RNG": 1000,
		"ATTACKS": {'':[],'evergreen_serpent':[]},
		"GRAVITY": True,
	},
	"covenant_follower": {
		"SPRITE SIZE": 96,
		"NAME": 'Covenant Follower',
		"HEALTH": 15,
		"EXP": 4,
		'DAMAGE': 3,
		"ATTACK_TYPE": 'wrath_of_alwyd',
		"SPEED": 2,
		"RESIST": 1,
		"ATK_CD": 800,
		"IFRAMES": 300,
		"ATK_RAD": 500,
		"AGR_RNG": 1500,
		"CAST_RNG": 600,
		"ATTACKS": {'':[],'wrath_of_alwyd':[]},
		"GRAVITY": True,
	},
	"sepparition": {
		"SPRITE SIZE": 160,
		"NAME": 'Sepparition',
		"HEALTH": 30,
		"EXP": 8,
		'DAMAGE': 5,
		"ATTACK_TYPE": 'soul_sever',
		"SPEED": 2,
		"RESIST": 2,
		"ATK_CD": 500,
		"IFRAMES": 500,
		"ATK_RAD": 300,
		"AGR_RNG": 1100,
		"ATTACKS": {'':[],'soul_sever':[]},
		"GRAVITY": False,
	}
}

""" SPELLS """
SPELLS = {
	# type		 size speed damage MGC
	'': [0, 0],
	'windblade': [96, 20, 5, 4],
	'fireball': [64, 10, 7, 5],
	'wrath_of_alwyd': [72, 15, 8, 10],
}


""" ITEMS """
ITEMS = {
	'magick': {
		'magick_shard': {
			"NAME": "MAGICK SHARD",
			"ANIM SPEED": 0.45,
			"SIZE": 32,
			"RECOV": 6,
			"TIME": 20,
			"PICKUP_RAD": 120
		}
	}
}
