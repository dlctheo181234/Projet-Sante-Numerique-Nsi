import pygame
import numpy as np
from btp import *
#from mapgen import Map
Map_Width = 1920
Map_Height = 1080
tile_size = 4
Lbat = []
W, H = Map_Width // tile_size, Map_Height // tile_size
pygame.init()


class Game:
    DEBUG = False  # Mettre à True pour activer le mode debug (dessin des hitboxes)
    def __init__(self):
        self.screen = pygame.display.set_mode((1920/1.5,1080/1.5), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("TEST EPIDEMIE")
        self.Lm =gen_list_btp(5, "maison", 20, 50)

    def draw(self):
        self.screen.fill((40, 40, 40))
        draw_scr()

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


def gen_list_btp(nb, type, w, h,):
    L = [] # liste de Mr Belgharbi
    for i in range(nb):
        a = Batiment(type, 0, 0, w, h) #Ils se démerdent après pour les coords.
        L.append(a)
        a.collide(Lbat)
    Lbat.append(L)
    print(L)
    return L

def draw_scr():        
        for sous_liste in Lbat:
            for bat in sous_liste:
                
                # Définir une couleur selon le type de bâtiment
                if bat.type == "maison":
                    couleur = (100, 150, 200)  # Bleu pour les maisons
                elif bat.type == "CC":
                    couleur = (200, 100, 100)
                
                # Calculer la position et la taille en tenant compte de tile_size
                rect = (
                    bat.x * tile_size, 
                    bat.y * tile_size, 
                    bat.w * tile_size, 
                    bat.h * tile_size
                )

                # Dessiner le rectangle sur l'écran
                pygame.draw.rect(game.screen, couleur, rect)
                
        # self.screen.blit(self.map.image, (0, 0))

if __name__ == '__main__':
    
    pygame.init()
    game= Game()
    game.run()
