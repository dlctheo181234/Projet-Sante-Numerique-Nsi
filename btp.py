import pygame as py
import random


class Batiment:
    def __init__(self, type, x, y, w, h):
        self.type = type
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __str__(self):
        return f"{self.type},{self.x}x,{self.y}y,{self.w}w,{self.h}h"

    def collide(self, l):
        collision = True
        while collision :
            collision = False
            for i in l :
                if i != self and abs(self.x - i.x) <= max(i.w, self.w) and abs(self.y - i.y) <= max(i.h, self.h):
                    # On donne de nouvelles coordonnées aléatoires (converties en entiers avec int())
                    self.x = random.randint(0, int(1920 / 1.5))
                    self.y = random.randint(0, int(1080 / 1.5))
                    collision = True
                    break
            if collision:
                break
        
