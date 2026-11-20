import pygame
import numpy as np

Map_Width = 1080
Map_Height = 1920

pygame.init()

class Game:
    DEBUG = False
    def __init__(self):
        self.screen = pygame.display.set_mode((1920,1080), pygame.RESIZABLE)
        


