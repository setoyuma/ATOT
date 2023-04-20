import pygame as pg

def main():
    pg.init()
    screen = pg.display.set_mode((1000,800),pg.FULLSCREEN)
    clock = pg.time.Clock()
    black = (0, 0, 0)
    move_combo = []
    frames_without_combo = 0


    while True:
        screen.fill('black')


        frames_without_combo += 1

        if frames_without_combo > 18 or len(move_combo) > 2:
            print("COMBO RESET")
            frames_without_combo = 0
            move_combo = []

        screen.fill(black)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                move_combo.append(event.key)  # Only keys for combos should be added

        if move_combo == [pg.K_DOWN, pg.K_RIGHT, pg.K_z]:
            print("FIRE BALL")
            frames_without_combo = 0
        print(move_combo)
        
        clock.tick(30)  # number of loops per second
        pg.display.update()

main()