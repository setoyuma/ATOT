import pygame as pg, sys
import random

class ParticlePrinciple:
    def __init__(self):
        self.particles = []
        self.colors = ["red","green","blue","yellow","purple"]
    
    def emit(self):
        # move/draw particles
        if self.particles:
            self.deleteParticles()
            for particle in self.particles:
                #move particle
                particle[0][1] += particle[2][1]
                particle[0][0] += particle[2][0]
                #shrink particle
                particle[1] -= 0.2
                #draw circle around particle
                pg.draw.circle(pg.display.get_surface(),pg.Color("White"),particle[0], int(particle[1]))
                # pg.draw.circle(pg.display.get_surface(),pg.Color(random.choice(self.colors)),particle[0], int(particle[1]))

    def addParticles(self, x, y):
        # adds particles
        posX = x
        posY = y
        # posX = pg.mouse.get_pos()[0]
        # posY = pg.mouse.get_pos()[1]
        radius = 4
        directionX = random.randint(-3,3)
        directionY = random.randint(-3,3)
        particleCircle = [[posX,posY], radius, [directionX, directionY]]
        self.particles.append(particleCircle)
    

    def deleteParticles(self):
        # remove particles after a certain time
        particleCopy = [particle for particle in self.particles if particle[1] > 0]
        self.particles = particleCopy
    

def main():
    pg.init()
    screen = pg.display.set_mode((800,800))
    pg.display.set_caption("particle test")
    clock = pg.time.Clock()
    FPS = 60
    particle1 = ParticlePrinciple()

    PARTICLE_EVENT = pg.USEREVENT + 1
    pg.time.set_timer(PARTICLE_EVENT,5)


    while True:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()


            if event.type == PARTICLE_EVENT:
                particle1.addParticles()
                particle1.addParticles()
                particle1.addParticles()
                particle1.addParticles()
                particle1.addParticles()
                particle1.addParticles()
                particle1.addParticles()
                particle1.addParticles()
            
            # if event.type == pg.MOUSEBUTTONDOWN:
            #     if event.button == 1:
            #         particle1.addParticles()

        screen.fill('black')
        particle1.emit()
        pg.display.flip()
        clock.tick(FPS)



if __name__ == '__main__':
    main()
