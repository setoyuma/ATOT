import pygame as pg, sys
from CONSTANTS import * 
from level import Level
from game_data import levels
from pygame.locals import KEYDOWN

# pg setup
def main():
	pg.init()
	screen = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
	pg.display.set_caption("ATOT")
	pg.display.set_icon(pg.image.load("./assets/logo.ico"))
	clock = pg.time.Clock()
	level = Level(levels[1])
	BG = pg.image.load('./assets/decoration/sky/DarkSky.png')

	while True:
		screen.fill('#0f0024')
		screen.blit(BG,(0,0))
		
		for event in pg.event.get():
			if event.type == pg.QUIT:
				print('\nGame Closed\n')
				pg.quit()
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == pg.K_f:
					pg.display.toggle_fullscreen()
				if event.key == pg.K_q:
					print('\nGame Closed\n')
					pg.quit()
					sys.exit()
				if event.key == pg.K_r:
					print('\nGame Restarting...\n')
					main()

		level.run()
		clock.tick(60)
		
		#show fps
		font = pg.font.Font(None,30)
		fpsCounter = str(int(clock.get_fps()))
		# print(fpsCounter)
		text = font.render(f"FPS: {fpsCounter}",True,'white','black')
		textPos = text.get_rect(centerx=1000, y=10)
		screen.blit(text,textPos)

		pg.display.update()

if __name__ == '__main__':
	main()