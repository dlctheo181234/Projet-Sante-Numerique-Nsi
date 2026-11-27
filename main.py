import pygame
import numpy as np
from mapgen import Map
Map_Width = 1920
Map_Height = 1080
tile_size = 4
W, H = Map_Width // tile_size, Map_Height // tile_size
pygame.init()


class Game:
    DEBUG = False  # Mettre à True pour activer le mode debug (dessin des hitboxes)
    def __init__(self):
        self.screen = pygame.display.set_mode((1920/1.5,1080/1.5), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("TEST EPIDEMIE")
        self.map = Map(W, H)

    def draw(self):
        self.screen.fill((40, 40, 40))
        #self.screen.blit(self.map.image, (0, 0))

    def run(self):
        running = True
        regen=False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.map.graine = np.random.randint(0, 1_000_000); regen = True
            if regen:
                    self.map.generer()
                    info = ""
            self.draw()

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == '__main__':
    
    pygame.init()
    game= Game()
    game.run()