import pygame as pg, sys
from CONSTANTS import * 
from level import Level
from game_data import levels
from pygame.locals import KEYDOWN

# pg setup
class Game:
	def __init__(self):
		pg.init()
		self.screen = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
		pg.display.set_caption("ATOT")
		pg.display.set_icon(pg.image.load("./assets/logo.ico"))
		self.clock = pg.time.Clock()
		self.dt = self.clock.tick(FPS)/1000.0
		self.level = Level(self, levels[1])
		self.BG = pg.image.load('./assets/decoration/sky/DarkSky.png')

	def main(self):
		while True:
			self.screen.fill('#0f0024')
			self.screen.blit(self.BG,(0,0))
			
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
						game = Game()
						game.main()

			self.level.run()
			self.clock.tick(FPS)
			
			#show fps
			font = pg.font.Font(None,30)
			fpsCounter = str(int(self.clock.get_fps()))
			# print(fpsCounter)
			text = font.render(f"FPS: {fpsCounter}",True,'white','black')
			textPos = text.get_rect(centerx=1000, y=10)
			self.screen.blit(text,textPos)

			pg.display.update()

if __name__ == '__main__':
	game = Game()
	game.main()