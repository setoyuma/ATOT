notes = {
	"Launcher" : "Added patch notes section, and character list.",
	"Game" : "Added decoration tiles and level system."
}

class_icons = {
	"paladin": './assets/UI/class-icons/paladin.png',
	"monk": './assets/UI/class-icons/monk.png'
}

projectile_types = {
	1: "windblade",
	2: "iceorb",
	3: "fireball",
}

classes = {
	# hp, str, mgck, def
	"monk": [4,6,10,3],
	"paladin": [6,8,7,12],
	"mistwalker": [4,5,8,6],
	"skolbinder": [5,5,11,10],
	"ebonguard": [8,8,5,10],
	"frostknight": [6,8,7,10],
	"technomancer": [7,2,10,8],
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
    'constraint': './level_data/data/world_0_constraint.csv',
    'terrain': './level_data/data/world_0_terrain.csv',
    'player': './level_data/data/world_0_player.csv',
    'deco': './level_data/data/world_0_deco.csv',
    'ground': './level_data/data/world_0_ground.csv',
    'trees': './level_data/data/world_0_trees.csv',
    'NPC': './level_data/data/world_0_NPC.csv',
    'items': './level_data/data/world_0_items.csv',
}

worlds = {
    1: world_0
}
