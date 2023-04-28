notes = {
	"Launcher" : "Added patch notes section, and character list.",
	"Game" : "Added decoration tiles and level system."
}

classes = {
	# hp, str, mgck, def
	"Monk": [4,6,10,3],
	"Paladin": [6,8,7,12],
	"Mistwalker": [4,5,8,6],
	"Skolbinder": [5,5,11,10],
	"Ebonguard": [8,8,5,10],
	"Frostknight": [6,8,7,10],
	"Technomancer": [7,2,10,8],
}

races = {
	# intellect, brutality, dexterity 
	"Voidkin": [5, 3, 2],
	"Misthelm": [3, 5, 5],
	"Ebonheart": [2, 6, 3],
	"Lightbringer": [6, 2, 3],
	"Skol": [2, 6, 5],
	"Weaver": [4, 2, 6],
	"Technoki": [6, 3, 6],
	"Celestial": [7, 1, 5],
	"Valkyrie": [4, 5, 3],
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
    'terrain': './level_data/data/world_0_terrain.csv',
    'player': './level_data/data/world_0_player.csv',
    'deco': './level_data/data/world_0_deco.csv',
    'ground': './level_data/data/world_0_ground.csv',
}

worlds = {
    1: world_0
}
