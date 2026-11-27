import pygame as py
import random


class Batiment:
    def __init__(self, type, x, y, w, h):
        self.type = type
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def collide(self, l):
        for i in l :
            for j in i :
                if abs(self.x - j.x) <= max(j.w, self.w) and abs(self.y - j.y) <= max(j.h, self.h) :
                    self.x = random.randint(0, 1920/1.5)
                    self.y = random.randint(0, 1080/1.5)
                    self.collide(l)
                    return
        return 

        
