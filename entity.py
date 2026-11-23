import pygame
import numpy
from dataclasses import dataclass

@dataclass
class entity:
    id: str
    type: str
    effects: list
    currentage: int
    maxage: int