import pygame
import numpy as np

Map_Width = 1080
Map_Height = 1920

class MapManager()
   [A faire] 

class Game:
    DEBUG = False  # Mettre à True pour activer le mode debug (dessin des hitboxes)
    def __init__(self):
        self.screen = pygame.display.set_mode((1920,1080), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("TEST EPIDEMIE")
        self.map_manager = MapManager(self.screen, self.player, self.DEBUG)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.map_manager.draw()

    def run(self):
        running = True

        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.VIDEORESIZE:
                    self.map_manager.on_resize()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.map_manager.reload_map(self.map_manager.map_path)
                    elif event.key == pygame.K_i:
                        self.map_manager.change_map()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            self.map_manager.update(0.5)
            self.draw()

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    
    pygame.init()
    game= Game()
    game.run()